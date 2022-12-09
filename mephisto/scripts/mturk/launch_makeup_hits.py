#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.task_run import TaskRun, TaskRunArgs
from mephisto.abstractions.providers.mturk.mturk_utils import (
    create_hit_type,
    email_worker,
    create_compensation_hit_with_hit_type,
    give_worker_qualification,
)

from omegaconf import OmegaConf
import json

from mephisto.data_model.assignment import (
    Assignment,
    InitializationData,
    AssignmentState,
)
from mephisto.data_model.unit import Unit
from mephisto.data_model.qualification import QUAL_EXISTS
from mephisto.utils.qualifications import make_qualification_dict
from mephisto.operations.task_launcher import COMPENSATION_UNIT_INDEX
from mephisto.abstractions.providers.mturk.mturk_provider import MTurkProviderArgs
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprintArgs
from mephisto.abstractions.architects.mock_architect import MockArchitectArgs
from mephisto.operations.hydra_config import MephistoConfig


def build_task_config(compensation_dict, requester):
    task_args = TaskRunArgs(
        task_title="Direct compensation task for requester issue",
        task_description=compensation_dict["reason"],
        task_reward=compensation_dict["amount"],
        task_tags="compensation,issue,repay",
    )

    provider_args = MTurkProviderArgs(
        requester_name=requester.requester_name,
    )

    blueprint_args = MockBlueprintArgs()
    architect_args = MockArchitectArgs()
    return MephistoConfig(
        provider=provider_args,
        blueprint=blueprint_args,
        architect=architect_args,
        task=task_args,
    )


def main():
    """
    Script to launch makeup tasks for workers that
    can't be bonused via other avenues.

    Creates a task for a worker, qualifying them directly,
    and marks as a soft_rejected HIT for the given task name.
    """
    db = LocalMephistoDB()

    task_name = input(
        "Please enter a task name for bookkeeping. This task name will be tied to "
        "the additional spend granted through this script, and should be the same "
        "as the task you originally launched that you now need to compensate for:\n>> "
    )
    tasks = db.find_tasks(task_name=task_name)
    if len(tasks) == 0:
        print("No tasks found with the given name...")
        all_tasks = db.find_tasks()
        all_names = set([t.task_name for t in all_tasks])
        print(f"Choose an existing task of {all_names} to use this functionality.")
        print(f"Compensation hits must be tied to an existing task")
        return 0
    task = tasks[0]

    req_name = input("Please enter an MTurkRequester name to use to bonus from:\n>> ")
    requesters = db.find_requesters(requester_name=req_name)
    if len(requesters) == 0:
        print("Could not find a requester by that name...")
        return 0
    requester = requesters[0]
    client = requester._get_client(requester._requester_name)

    print(
        "You can now enter a worker id, amount, and reason for as many compensation tasks "
        "as you want to launch for this."
    )
    compensation_hits = []
    amount = None
    reason = None
    while True:
        worker_id = input(
            "Enter a worker id to compensate. Leave blank to move on to launching: \n>> "
        ).strip()
        if len(worker_id) == 0:
            break
        prev_amount = "" if amount is None else f" (leave blank for ${amount})"
        next_amount = input(
            f"Enter the amount in dollars to pay out in this compensation task{prev_amount}:\n>> $"
        )
        amount = float(next_amount) if len(next_amount.strip()) != 0 else amount
        assert amount is not None, "Amount can not be left blank"
        prev_reason = "" if reason is None else f" (leave blank for '{reason}'"
        next_reason = input(
            f"Provide reason for launching this compensation task. This will be sent to the worker{prev_reason}:\n>> "
        )
        reason = next_reason if len(next_reason.strip()) != 0 else reason
        assert reason is not None, "Reason can not be left blank"
        compensation_hits.append(
            {
                "worker_id": worker_id,
                "amount": amount,
                "reason": reason,
            }
        )
    if len(compensation_hits) == 0:
        print("No compensation details provided, exiting")
        return 0

    print(f"You entered the following tasks:\n{compensation_hits}")
    input("Input anything to confirm and continue...")

    # Iterate through and launch tasks
    for comp_dict in compensation_hits:
        # Create the MTurk qualification for this specific worker
        worker_id = comp_dict["worker_id"]
        qual_name = f"compensation-for-{worker_id}-on-{task_name}"
        print(f"Creating qualification for {worker_id}: {qual_name}....")
        qualification = make_qualification_dict(qual_name, QUAL_EXISTS, None)
        qual_map = requester.datastore.get_qualification_mapping(qual_name)
        if qual_map is None:
            qualification[
                "QualificationTypeId"
            ] = requester._create_new_mturk_qualification(qual_name)
        else:
            qualification["QualificationTypeId"] = qual_map["mturk_qualification_id"]
        give_worker_qualification(
            client, worker_id, qualification["QualificationTypeId"]
        )

        # Create the task run for this HIT
        print(f"Creating task run and data model components for this HIT")
        config = build_task_config(comp_dict, requester)
        init_params = OmegaConf.to_yaml(OmegaConf.structured(config))
        new_run_id = db.new_task_run(
            task.db_id,
            requester.db_id,
            json.dumps(init_params),
            requester.provider_type,
            "mock",
            requester.is_sandbox(),
        )
        task_run = TaskRun.get(db, new_run_id)

        # Create an assignment, unit, agent, and mark as assigned
        # Assignment creation
        task_args = task_run.get_task_args()
        assignment_id = db.new_assignment(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            task_run.task_type,
            task_run.provider_type,
            task_run.sandbox,
        )
        data = InitializationData({}, [{}])
        assignment = Assignment.get(db, assignment_id)
        assignment.write_assignment_data(data)

        # Unit creation
        unit_id = db.new_unit(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            assignment_id,
            COMPENSATION_UNIT_INDEX,
            task_args.task_reward,
            task_run.provider_type,
            task_run.task_type,
            task_run.sandbox,
        )
        compensation_unit = Unit.get(db, unit_id)
        print(f"Created {task_run}, {assignment}, and {compensation_unit}...")

        # Set up HIT type
        hit_type_id = create_hit_type(
            client,
            task_run.get_task_args(),
            [qualification],
            auto_approve_delay=30,
            skip_locale_qual=True,
        )

        # Create the task on MTurk, email the worker
        print("Creating and deploying task on MTurk")
        duration = 60 * 60 * 24
        run_id = task_run.db_id
        hit_link, hit_id, response = create_compensation_hit_with_hit_type(
            client, comp_dict["reason"], hit_type_id
        )
        requester.datastore.new_hit(hit_id, hit_link, duration, task_run.db_id)

        print("Sending email to worker...")
        result = email_worker(
            client,
            worker_id,
            "Compensation HIT Launched",
            (
                "Hello Worker,\n We've launched a compensation hit for a task that you've worked on "
                f"for us in the past. The reason supplied for this task was: {reason}. This task is "
                f"only doable by you, and should reward ${comp_dict['amount']}. Thanks for being a valued "
                "contributor to our tasks, and for allowing us to try and resolve the issue.\n\n"
                f"Your task can be accessed at the following link: {hit_link}."
            ),
        )

        if not result[0]:
            print(
                f"Email send failed, for reason {result[1]}\n"
                f"Please send {hit_link} to {worker_id} yourself if they reached out about this issue."
            )

        # Mark the agent as soft_rejected, such that we've "paid" it
        compensation_unit.set_db_status(AssignmentState.SOFT_REJECTED)


if __name__ == "__main__":
    main()
