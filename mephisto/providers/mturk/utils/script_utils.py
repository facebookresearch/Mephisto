#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Optional

from mephisto.providers.mturk.mturk_utils import give_worker_qualification
from mephisto.core.local_database import LocalMephistoDB
from mephisto.data_model.requester import Requester


def direct_soft_block_mturk_workers(
    worker_list: List[str],
    soft_block_qual_name: str,
    requester_name: Optional[str] = None,
):
    db = LocalMephistoDB()
    reqs = db.find_requesters(requester_name=requester_name, provider_type="mturk")
    requester = reqs[0]

    mturk_qual_details = requester.datastore.get_qualification_mapping(
        soft_block_qual_name
    )
    if mturk_qual_details is not None:
        # Overrule the requester, as this qualification already exists
        requester = Requester(db, mturk_qual_details["requester_id"])
        qualification_id = mturk_qual_details["mturk_qualification_id"]
    else:
        qualification_id = requester._create_new_mturk_qualification(
            soft_block_qual_name
        )

    mturk_client = requester._get_client(requester._requester_name)
    for worker_id in worker_list:
        give_worker_qualification(mturk_client, worker_id, qualification_id, value=1)
