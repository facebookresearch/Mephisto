#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Utility script that finds, expires, and disposes HITs that may not
have been taking down during a run that exited improperly.
"""
from mephisto.abstractions.providers.mturk.mturk_utils import (
    get_outstanding_hits,
    expire_and_dispose_hits,
)
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.mturk.mturk_requester import MTurkRequester
from datetime import datetime, timedelta

from typing import List, Dict, Any, Optional


def main():
    db = LocalMephistoDB()

    all_requesters = db.find_requesters(provider_type="mturk")
    all_requesters += db.find_requesters(provider_type="mturk_sandbox")

    print("You have the following requesters available for mturk and mturk sandbox:")
    r_names = [r.requester_name for r in all_requesters]
    print(sorted(r_names))

    use_name = input("Enter the name of the requester to clear HITs from:\n>> ")
    while use_name not in r_names:
        use_name = input(
            f"Sorry, {use_name} is not in the requester list. "
            f"The following are valid: {r_names}\n"
            f"Select one:\n>> "
        )

    requester = db.find_requesters(requester_name=use_name)[0]
    assert isinstance(requester, MTurkRequester)
    client = requester._get_client(requester._requester_name)

    outstanding_hit_types = get_outstanding_hits(client)
    num_hit_types = len(outstanding_hit_types.keys())
    sum_hits = sum(
        [len(outstanding_hit_types[x]) for x in outstanding_hit_types.keys()]
    )

    all_hits: List[Dict[str, Any]] = []
    for hit_type in outstanding_hit_types.keys():
        all_hits += outstanding_hit_types[hit_type]

    broken_hits = [
        h
        for h in all_hits
        if h["NumberOfAssignmentsCompleted"] == 0 and h["HITStatus"] != "Reviewable"
    ]

    print(
        f"The requester {use_name} has {num_hit_types} outstanding HIT "
        f"types, with {len(broken_hits)} suspected active or broken HITs.\n"
        "This may include tasks that are still in-flight, but also "
        "tasks that have already expired but have not been disposed of yet."
    )

    run_type = input(
        "Would you like to cleanup by (t)itle, clean up (o)ld tasks (> 2 weeks), or just clean up (a)ll?\n>> "
    )
    use_hits: Optional[List[Dict[str, Any]]] = None

    while use_hits is None:
        if run_type.lower().startswith("t"):
            use_hits = []
            for hit_type in outstanding_hit_types.keys():
                cur_title = outstanding_hit_types[hit_type][0]["Title"]
                creation_time = outstanding_hit_types[hit_type][0]["CreationTime"]
                creation_time_str = creation_time.strftime("%m/%d/%Y, %H:%M:%S")
                print(f"HIT TITLE: {cur_title}")
                print(f"LAUNCH TIME: {creation_time_str}")
                print(f"HIT COUNT: {len(outstanding_hit_types[hit_type])}")
                should_clear = input(
                    "Should we cleanup this hit type? (y)es for yes, anything else for no: "
                    "\n>> "
                )
                if should_clear.lower().startswith("y"):
                    use_hits += outstanding_hit_types[hit_type]
        elif run_type.lower().startswith("a"):
            use_hits = all_hits
        elif run_type.lower().startswith("o"):
            old_cutoff = datetime.now(all_hits[0]["CreationTime"].tzinfo) - timedelta(
                days=14
            )
            use_hits = [h for h in all_hits if h["CreationTime"] < old_cutoff]
        else:
            run_type = input("Options are (t)itle, (o)ld, or (a)ll:\n>> ")

    print(f"Disposing {len(use_hits)} HITs.")
    remaining_hits = expire_and_dispose_hits(client, use_hits)

    if len(remaining_hits) == 0:
        print("Disposed!")
    else:
        print(
            f"After disposing, {len(remaining_hits)} could not be disposed.\n"
            f"These may not have been reviewed yet, or are being actively worked on.\n"
            "They have been expired though, so please try to dispose later."
            "The first 20 dispose errors are added below:"
        )
        print([h["dispose_exception"] for h in remaining_hits[:20]])


if __name__ == "__main__":
    main()
