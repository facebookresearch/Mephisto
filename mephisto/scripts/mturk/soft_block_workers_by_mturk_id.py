#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.providers.mturk.utils.script_utils import (
    direct_soft_block_mturk_workers,
)

from mephisto.abstractions.databases.local_database import LocalMephistoDB


def main():
    db = LocalMephistoDB()
    reqs = db.find_requesters(provider_type="mturk")
    names = [r.requester_name for r in reqs]
    print("Available Requesters: ", names)

    requester_name = input("Select a requester to soft block from: ")
    soft_block_qual_name = input("Provide a soft blocking qualification name: ")

    workers_to_block = []
    while True:
        new_id = input("MTurk Worker Id to soft block (blank to block all entered): ")
        if len(new_id.strip()) == 0:
            break
        workers_to_block.append(new_id)

    direct_soft_block_mturk_workers(
        db, workers_to_block, soft_block_qual_name, requester_name
    )


if __name__ == "__main__":
    main()
