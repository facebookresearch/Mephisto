#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Utility script that finds, HITs associated with a specific task run,
and tries to get their information
"""

from mephisto.abstractions.providers.mturk.mturk_datastore import MTurkDatastore
from mephisto.abstractions.providers.mturk.mturk_requester import MTurkRequester
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.task_run import TaskRun

from typing import cast


def main():
    task_run_id = input("Please enter the task_run_id you'd like to check: ")
    db = LocalMephistoDB()
    task_run = TaskRun.get(db, task_run_id)
    requester = task_run.get_requester()
    if not isinstance(requester, MTurkRequester):
        print(
            "Must be checking a task launched on MTurk, this one uses the following requester:"
        )
        print(requester)
        exit(0)

    turk_db = db.get_datastore_for_provider("mturk")
    hits = turk_db.get_unassigned_hit_ids(task_run_id)

    print(f"Found the following HIT ids unassigned: {hits}")

    # print all of the HITs found above
    from mephisto.abstractions.providers.mturk.mturk_utils import get_hit

    for hit_id in hits:
        hit_info = get_hit(requester._get_client(requester._requester_name), hits[0])
        print(f"MTurk HIT data for {hit_id}:\n{hit_info}\n")


if __name__ == "__main__":
    main()
