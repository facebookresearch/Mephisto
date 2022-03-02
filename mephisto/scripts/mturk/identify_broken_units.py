#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.task_run import TaskRun
from mephisto.abstractions.providers.mturk.mturk_utils import (
    get_assignments_for_hit,
    get_outstanding_hits,
)


def main():
    """
    Script to crawl through the database for a specific task run and ensure that
    all of the states of units and related MTurk data is synced up.
    """
    TASK_RUN = input("Enter task run ID to check integrity of: \n")
    db = LocalMephistoDB()
    task_run = TaskRun(db, TASK_RUN)

    units = task_run.get_units()

    completed_agentless_units = [
        u
        for u in units
        if u.get_status() in ["completed", "accepted", "soft_rejected"]
        and u.get_assigned_agent() is None
    ]
    completed_agented_units = [
        u
        for u in units
        if u.get_status() in ["completed", "accepted", "soft_rejected"]
        and u.get_assigned_agent() is not None
    ]
    completed_timeout_units = [
        u
        for u in completed_agented_units
        if u.get_assigned_agent().get_status() == "timeout"
    ]

    if len(completed_agentless_units) == 0 and len(completed_timeout_units) == 0:
        print("It appears everything is as should be!")
        return

    print(
        f"Found {len(completed_agentless_units)} completed units without an agent, and "
        f"{len(completed_timeout_units)} completed units with a timed out agent.\n"
        "We'll need to query MTurk HITs to determine where these fall..."
    )
    print(completed_timeout_units[-5:])

    agents = db.find_agents(task_run_id=TASK_RUN) + db.find_agents(
        task_run_id=TASK_RUN - 1
    )
    requester = units[0].get_requester()
    client = requester._get_client(requester._requester_name)

    outstanding = get_outstanding_hits(client)
    print(
        f"Found {len(outstanding)} different HIT types in flight for this account. "
        "Select the relevant one below."
    )
    for hit_type_id, hits in outstanding.items():
        print(f"{hit_type_id}({len(hits)} hits): {hits[0]['Title']}")
        if input("Is this correct?: y/(n) ").lower().startswith("y"):
            break

    task_hits = outstanding[hit_type_id]

    print(f"Querying assignments for the {len(hits)} tasks.")

    task_assignments_uf = [
        get_assignments_for_hit(client, h["HITId"]) for h in task_hits
    ]
    task_assignments = [t[0] for t in task_assignments_uf if len(t) != 0]

    print(f"Found {len(task_assignments)} assignments to map.")

    print("Constructing worker-to-agent mapping...")
    worker_id_to_agents = {}
    for a in agents:
        worker_id = a.get_worker().worker_name
        if worker_id not in worker_id_to_agents:
            worker_id_to_agents[worker_id] = []
        worker_id_to_agents[worker_id].append(a)

    print("Constructing hit-id to unit mapping for completed...")
    hit_ids_to_unit = {
        u.get_mturk_hit_id(): u for u in units if u.get_mturk_hit_id() is not None
    }

    unattributed_assignments = [
        t for t in task_assignments if t["HITId"] not in hit_ids_to_unit
    ]

    print(f"Found {len(unattributed_assignments)} assignments with no mapping!")

    print(f"Mapping unattributed assignments to workers")

    for assignment in unattributed_assignments:
        worker_id = assignment["WorkerId"]
        agents = worker_id_to_agents.get(worker_id)
        print(f"Worker: {worker_id}. Current agents: {agents}")
        if agents is not None:
            for agent in agents:
                if agent.get_status() != "timeout":
                    continue

                units_agent = agent.get_unit().get_assigned_agent()
                if units_agent is None or units_agent.db_id != agent.db_id:
                    continue

                print(
                    f"Agent {agent} would be a good candidate to reconcile {assignment['HITId']}"
                )
                # TODO(WISH) automate the below
                print(
                    "You can do this manually by selecting the best candidate, then "
                    "updating the MTurk datastore to assign this HITId and assignmentId "
                    "to the given agent and its associated unit. You can then either "
                    "approve if you can reconcile the agent state, or soft_reject "
                    "to pay out properly. "
                )

    do_cleanup = input(
        f"If all are reconciled, would you like to clean up remaining timeouts? y/(n)"
    )
    if do_cleanup.lower().startswith("y"):
        for unit in completed_agentless_units:
            unit.set_db_status("expired")
        for unit in completed_timeout_units:
            unit.set_db_status("expired")


if __name__ == "__main__":
    main()
