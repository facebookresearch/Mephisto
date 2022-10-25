#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Optional, TYPE_CHECKING, Dict

from mephisto.abstractions.providers.mturk.mturk_utils import give_worker_qualification
from mephisto.abstractions.providers.mturk.mturk_requester import MTurkRequester
from mephisto.data_model.requester import Requester
from mephisto.data_model.unit import Unit
from tqdm import tqdm  # type: ignore
from mephisto.utils.logger_core import get_logger

logging = get_logger(name=__name__)

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB


def direct_assign_qual_mturk_workers(
    db: "MephistoDB",
    worker_list: List[str],
    qual_name: str,
    requester_name: Optional[str] = None,
):
    """
    Directly assign MTurk qualification that Mephisto associates with qual_name
    to all of the MTurk worker ids in worker_list. If requester_name is not provided,
    it will use the most recently registered mturk requester in the database.
    """
    reqs = db.find_requesters(requester_name=requester_name, provider_type="mturk")
    requester = reqs[-1]

    assert isinstance(
        requester, MTurkRequester
    ), "Can only direct soft block mturk workers from mturk requester"

    mturk_qual_details = requester.datastore.get_qualification_mapping(qual_name)
    if mturk_qual_details is not None:
        # Overrule the requester, as this qualification already exists
        requester = Requester.get(db, mturk_qual_details["requester_id"])
        qualification_id = mturk_qual_details["mturk_qualification_id"]
    else:
        qualification_id = requester._create_new_mturk_qualification(qual_name)

    assert isinstance(
        requester, MTurkRequester
    ), "Can only direct assign qualification (soft block) mturk workers from mturk requester"
    mturk_client = requester._get_client(requester._requester_name)
    for worker_id in tqdm(worker_list):
        try:
            give_worker_qualification(
                mturk_client, worker_id, qualification_id, value=1
            )
        except Exception as e:
            logging.exception(
                f'Failed to give worker with ID: "{worker_id}" qualification with error: {e}. Skipping.'
            )


def direct_soft_block_mturk_workers(
    db: "MephistoDB",
    worker_list: List[str],
    soft_block_qual_name: str,
    requester_name: Optional[str] = None,
):
    """
    Directly assign the soft blocking MTurk qualification that Mephisto
    associates with soft_block_qual_name to all of the MTurk worker ids
    in worker_list. If requester_name is not provided, it will use the
    most recently registered mturk requester in the database.
    """
    direct_assign_qual_mturk_workers(
        db=db,
        worker_list=worker_list,
        qual_name=soft_block_qual_name,
        requester_name=requester_name,
    )


def get_mturk_ids_from_unit_id(db, unit_id: str) -> Dict[str, Optional[str]]:
    """
    Find the relevant mturk ids from the given mephisto unit id
    """
    mturk_unit = Unit.get(db, unit_id)
    assignment_id = mturk_unit.get_mturk_assignment_id()
    hit_id = mturk_unit.get_mturk_hit_id()
    agent = mturk_unit.get_assigned_agent()
    worker_id = None
    if agent is not None:
        worker_id = agent.get_worker().get_mturk_worker_id()
    return {"assignment_id": assignment_id, "hit_id": hit_id, "worker_id": worker_id}
