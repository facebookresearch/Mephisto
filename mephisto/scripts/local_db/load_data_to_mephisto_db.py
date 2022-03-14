#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Utility script that directly loads in data from another place to
the MephistoDB under a specified task run, using MockRequester and
MockWorkers as we don't know where the data actually came from.

!! Currently in development, not necessarily for use !!
"""

from mephisto.abstractions.blueprints.static_react_task.static_react_blueprint import (
    StaticReactBlueprint,
    BLUEPRINT_TYPE_STATIC_REACT,
)
from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.blueprints.abstract.static_task.static_agent_state import (
    StaticAgentState,
)
from mephisto.abstractions.providers.mock.mock_requester import MockRequester
from mephisto.abstractions.providers.mock.mock_worker import MockWorker
from mephisto.abstractions.providers.mock.mock_agent import MockAgent
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.assignment import Assignment, InitializationData
from mephisto.data_model.unit import Unit
from mephisto.data_model.agent import Agent
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.task_run import TaskRun

from typing import List, Dict, Any, cast

import json


def main():
    db = LocalMephistoDB()

    # Get the requester that the run will be requested from
    all_requesters = db.find_requesters(provider_type="mock")

    print("You have the following requesters available for use on mock:")
    r_names = [r.requester_name for r in all_requesters]
    print(sorted(r_names))

    use_name = input("Enter the name of the requester to use, or a new requester:\n>> ")
    while use_name not in r_names:
        confirm = input(
            f"{use_name} is not in the requester list. "
            f"Would you like to create a new MockRequester with this name? (y)/n > "
        )
        if confirm.lower().startswith("n"):
            use_name = input(f"Okay, enter another name from {r_names} \n >> ")
        else:
            MockRequester.new(db, use_name)
            r_names.append(use_name)

    requester = db.find_requesters(provider_type="mock", requester_name=use_name)[0]

    # Get the worker that will be acting as the worker on this task
    all_workers = db.find_workers(provider_type="mock")
    print("You have the following workers available for use on mock:")
    w_names = [r.worker_name for r in all_workers]
    print(sorted(w_names))

    use_name = input("Enter the name of the worker to use, or a new worker:\n>> ")
    while use_name not in w_names:
        confirm = input(
            f"{use_name} is not in the worker list. "
            f"Would you like to create a new MockWorker with this name? (y)/n > "
        )
        if confirm.lower().startswith("n"):
            use_name = input(f"Okay, enter another name from {w_names} \n >> ")
        else:
            MockWorker.new(db, use_name)
            w_names.append(use_name)

    worker = db.find_workers(provider_type="mock", worker_name=use_name)[0]

    # Get or create a task run for this
    tasks = db.find_tasks()
    task_names = [
        t.task_name for t in tasks if t.task_type == BLUEPRINT_TYPE_STATIC_REACT
    ]
    print(f"Use an existing run? ")

    print(f"You have the following existing mock runs:")
    print(sorted(task_names))

    use_name = input("Enter the name of the task_run to use, or make a new one:\n>> ")
    while use_name not in task_names:
        confirm = input(
            f"{use_name} is not in the task name list. "
            f"Would you like to create a new TaskRun with this name? (y)/n > "
        )
        if confirm.lower().startswith("n"):
            use_name = input(f"Okay, enter another name from {task_names} \n >> ")
        else:
            task_id = db.new_task(use_name, BLUEPRINT_TYPE_STATIC_REACT)
            task_names.append(use_name)
            task_run_id = db.new_task_run(
                task_id,
                requester.db_id,
                json.dumps({}),
                "mock",
                BLUEPRINT_TYPE_STATIC_REACT,
                requester.is_sandbox(),
            )
            task_run = TaskRun.get(db, task_run_id)

    tasks = db.find_tasks(task_name=use_name)
    valid_tasks = [t for t in tasks if t.task_type == BLUEPRINT_TYPE_STATIC_REACT]
    task_run = db.find_task_runs(task_id=valid_tasks[0].db_id)[0]

    print(f"Found task run: {task_run}")

    test_annotations: List[Dict[str, Any]] = [
        {
            "inputs": {"something": True, "something else": False},
            "outputs": {"some": "annotations"},
        }
    ]

    # Write a new task, and then complete it
    for annotation in test_annotations:
        assignment_id = db.new_assignment(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            task_run.task_type,
            task_run.provider_type,
            task_run.sandbox,
        )
        assignment = Assignment.get(db, assignment_id)
        assignment.write_assignment_data(
            InitializationData(unit_data=[{}], shared=annotation["inputs"])
        )

        unit_id = db.new_unit(
            task_run.task_id,
            task_run.db_id,
            task_run.requester_id,
            assignment_id,
            0,  # Unit_index
            0,  # reward
            task_run.provider_type,
            task_run.task_type,
            task_run.sandbox,
        )

        unit = Unit.get(db, unit_id)
        agent = MockAgent.new(db, worker, unit)
        agent_state = cast("StaticAgentState", agent.state)
        agent_state.state["inputs"] = annotation["inputs"]
        agent_state.state["outputs"] = annotation["outputs"]
        agent.state.save_data()
        agent.mark_done()
        agent.update_status(AgentState.STATUS_COMPLETED)

    # Show tasks appear in MephistoDB:
    mephisto_data_browser = MephistoDataBrowser(db=db)
    units = mephisto_data_browser.get_units_for_task_name(input("Input task name: "))
    for unit in units:
        print(mephisto_data_browser.get_data_from_unit(unit))


if __name__ == "__main__":
    main()
