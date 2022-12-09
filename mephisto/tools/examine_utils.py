#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Utilities specifically for running examine scripts. Example usage can be
seen in the examine results scripts in the examples directory.
"""

from mephisto.tools.data_browser import DataBrowser
from mephisto.data_model.worker import Worker
from mephisto.utils.qualifications import find_or_create_qualification
import traceback

from typing import TYPE_CHECKING, Optional, Tuple, Callable, Dict, Any, List

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.unit import Unit


def _get_and_format_data(
    data_browser: "DataBrowser",
    format_data_for_printing: Callable[[Dict[str, Any]], str],
    unit: "Unit",
) -> str:
    """
    Safetly wrapped function to extract the display data string for a specific unit.
    Catches and prints any exceptions.
    """
    formatted = "Error formatting data, see above..."
    try:
        data = data_browser.get_data_from_unit(unit)
        try:
            formatted = format_data_for_printing(data)
        except Exception as e:
            print(f"Unexpected error formatting data for {unit}: {e}")
            # Print the full exception, as this could be user error on the
            # formatting function
            traceback.print_exc()
    except Exception as e:
        print(f"Unexpected error getting data for {unit}: {e}")
    return formatted


def print_results(
    db: "MephistoDB",
    task_name: str,
    format_data_for_printing: Callable[[Dict[str, Any]], str],
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> None:
    """
    Script to write out to stdout from start to end results from the task with the given task name
    """
    data_browser = DataBrowser(db=db)
    units = data_browser.get_units_for_task_name(task_name)
    if end is None:
        end = len(units)
    if start is None:
        start = 0
    units.reverse()
    for unit in units[start:end]:
        print(_get_and_format_data(data_browser, format_data_for_printing, unit))


def prompt_for_options(
    task_name: Optional[str] = None,
    block_qualification: Optional[str] = None,
    approve_qualification: Optional[str] = None,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Utility to request common user options for examine scripts.
    Leave `block_qualification` or `approve_qualification` as empty strings
    to skip their respective prompt.
    """
    if task_name is None:
        task_name = input("Input task name: ")
    if block_qualification is None:
        block_qualification = input(
            "If you'd like to soft-block workers, you'll need a block qualification. "
            "Leave blank otherwise.\nEnter block qualification: "
        )
    if approve_qualification is None:
        approve_qualification = input(
            "If you'd like to qualify high-quality workers, you'll need an approve "
            "qualification. Leave blank otherwise.\nEnter approve qualification: "
        )
    if len(block_qualification.strip()) == 0:
        block_qualification = None
    if len(approve_qualification.strip()) == 0:
        approve_qualification = None
    input(
        "Starting review with following params:\n"
        f"Task name: {task_name}\n"
        f"Blocking qualification: {block_qualification}\n"
        f"Approve qualification: {approve_qualification}\n"
        "Press enter to continue... "
    )
    return task_name, block_qualification, approve_qualification


def get_worker_stats(units: List["Unit"]) -> Dict[str, Dict[str, List["Unit"]]]:
    """
    Traverse a list of units and create a mapping from worker id
    to their units, grouped by their current status
    """
    previous_work_by_worker: Dict[str, Dict[str, List["Unit"]]] = {}
    for unit in units:
        w_id = unit.worker_id
        if w_id not in previous_work_by_worker:
            previous_work_by_worker[w_id] = {
                "accepted": [],
                "soft_rejected": [],
                "rejected": [],
            }
        previous_work_by_worker[w_id][unit.get_status()].append(unit)
    return previous_work_by_worker


def format_worker_stats(
    worker_id: str, previous_work_by_worker: Dict[str, Dict[str, List["Unit"]]]
) -> str:
    """
    When given a worker id and a list of worker stats, return a string
    containing the proportion of accepted to rejected work.
    """
    prev_work = previous_work_by_worker.get(worker_id)
    if prev_work is None:
        return "(First time worker!)"
    accepted_work = len(prev_work["accepted"])
    soft_rejected_work = len(prev_work["soft_rejected"])
    rejected_work = len(prev_work["rejected"])
    return f"({accepted_work} | {rejected_work + soft_rejected_work}({soft_rejected_work}) / {accepted_work + soft_rejected_work + rejected_work})"


def run_examine_by_worker(
    db: "MephistoDB",
    format_data_for_printing: Callable[[Dict[str, Any]], str],
    task_name: Optional[str] = None,
    block_qualification: Optional[str] = None,
    approve_qualification: Optional[str] = None,
):
    """
    Basic script for reviewing work, grouped by worker for convenience. First gets
    the required information to run a review, then
    """
    data_browser = DataBrowser(db=db)

    # Get initial arguments
    if task_name is None:
        task_name, block_qualification, approve_qualification = prompt_for_options(
            task_name, block_qualification, approve_qualification
        )

    tasks = db.find_tasks(task_name=task_name)
    assert len(tasks) >= 1, f"No task found under name {task_name}"

    print(
        "You will be reviewing actual tasks with this flow. Tasks that you either Accept or Pass "
        "will be paid out to the worker, while rejected tasks will not. Passed tasks will be "
        "specially marked such that you can leave them out of your dataset. \n"
        "You may enter the option in caps to apply it to the rest of the units for a given worker."
    )
    if block_qualification is not None:
        created_block_qual = find_or_create_qualification(db, block_qualification)
        print(
            "When you pass or reject a task, the script gives you an option to disqualify the worker "
            "from future tasks by assigning a qualification. If provided, this worker will no "
            "longer be able to work on tasks where the set --block-qualification shares the same name "
            f"you provided above: {block_qualification}\n"
        )
    if approve_qualification is not None:
        created_approve_qual = find_or_create_qualification(db, approve_qualification)
        print(
            "You may use this script to establish a qualified worker pool by granting the provided "
            f"approve qualification {approve_qualification} to workers you think understand the task "
            "well. This will be provided as an option for workers you (A)pprove all on. "
            "Future tasks can use this qual as a required qualification, as described in the "
            "common qualification flows document."
        )
    print(
        "**************\n"
        "You should only reject tasks when it is clear the worker has acted in bad faith, and "
        "didn't actually do the task. Prefer to pass on tasks that were misunderstandings.\n"
        "**************\n"
    )

    units = data_browser.get_units_for_task_name(task_name)

    others = [u for u in units if u.get_status() != "completed"]
    units = [u for u in units if u.get_status() == "completed"]
    reviews_left = len(units)
    previous_work_by_worker = get_worker_stats(others)

    # Determine allowed options
    options = ["a", "p", "r"]
    options_string = "Do you want to accept this work? (a)ccept, (r)eject, (p)ass:"

    units_by_worker: Dict[str, List["Unit"]] = {}

    for u in units:
        w_id = u.worker_id
        if w_id not in units_by_worker:
            units_by_worker[w_id] = []
        units_by_worker[w_id].append(u)

    # Run the review
    for w_id, w_units in units_by_worker.items():
        worker = Worker.get(db, w_id)
        worker_name = worker.worker_name
        apply_all_decision = None
        reason = None
        for idx, unit in enumerate(w_units):

            print(
                f"Reviewing for worker {worker_name}, ({idx+1}/{len(w_units)}), "
                f"Previous {format_worker_stats(w_id, previous_work_by_worker)} "
                f"(total remaining: {reviews_left})"
            )
            reviews_left -= 1
            print(format_data_for_printing(data_browser.get_data_from_unit(unit)))
            if apply_all_decision is not None:
                decision = apply_all_decision
            else:
                decision = input(
                    "Do you want to accept this work? (a)ccept, (r)eject, (p)ass: "
                )
            while decision.lower() not in options:
                decision = input(
                    "Decision must be one of a, p, r. Use CAPS to apply to all remaining for worker: "
                )

            agent = unit.get_assigned_agent()
            assert (
                agent is not None
            ), f"Can't make decision on None agent... issue with {unit}"
            if decision.lower() == "a":
                agent.approve_work()
                if decision == "A" and approve_qualification is not None:
                    should_special_qualify = input(
                        "Do you want to approve qualify this worker? (y)es/(n)o: "
                    )
                    if should_special_qualify.lower() in ["y", "yes"]:
                        worker.grant_qualification(approve_qualification, 1)
            elif decision.lower() == "p":
                agent.soft_reject_work()
                if apply_all_decision is None and block_qualification is not None:
                    should_soft_block = input(
                        "Do you want to soft block this worker? (y)es/(n)o: "
                    )
                    if should_soft_block.lower() in ["y", "yes"]:
                        worker.grant_qualification(block_qualification, 1)
            else:  # decision = 'r'
                if apply_all_decision is None:
                    reason = input("Why are you rejecting this work? ")
                    should_block = input(
                        "Do you want to hard block this worker? (y)es/(n)o: "
                    )
                    if should_block.lower() in ["y", "yes"]:
                        block_reason = input("Why permanently block this worker? ")
                        worker.block_worker(block_reason)
                agent.reject_work(reason)

            if decision.lower() != decision:
                apply_all_decision = decision.lower()


def run_examine_or_review(
    db: "MephistoDB",
    format_data_for_printing: Callable[[Dict[str, Any]], str],
) -> None:
    do_review = input(
        "Do you want to (r)eview, or (e)xamine data? Default "
        "examine. Can put e <end> or e <start> <end> to choose "
        "how many to view\n"
    )

    if do_review.lower().startswith("r"):
        run_examine_by_worker(db, format_data_for_printing)
    else:
        start = 0
        end = 15
        opts = do_review.split(" ")
        if len(opts) == 2:
            end = int(opts[1])
        elif len(opts) == 3:
            start = int(opts[1])
            end = int(opts[2])
        task_name = input("Input task name: ")
        print_results(db, task_name, format_data_for_printing, start=start, end=end)
