#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from datetime import datetime

from mephisto.data_model.assignment import Unit
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.data_model.blueprint import AgentState
from mephisto.providers.mturk.mturk_utils import (
    expire_hit,
    get_hit,
    create_hit_with_hit_type,
)
from mephisto.providers.mturk.provider_type import PROVIDER_TYPE
from typing import List, Optional, Tuple, Dict, Any, Type, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.assignment import Assignment
    from mephisto.providers.mturk.mturk_requester import MTurkRequester
    from mephisto.providers.mturk.mturk_datastore import MTurkDatastore

# TODO Fill in the duration with the task duration
TODO_FILL_DURATION = 500


class MTurkUnit(Unit):
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment. It is the smallest 'unit' of work to complete
    the assignment, and this class is only responsible for checking
    the status of that work itself being done.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            self.PROVIDER_TYPE
        )
        self._sync_hit_mapping()
        self.__requester: Optional["MTurkRequester"] = None

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    def _sync_hit_mapping(self) -> None:
        """Sync with the datastore to see if any mappings have updated"""
        try:
            mapping = self.datastore.get_hit_mapping(self.db_id)
            self.hit_id = mapping["hit_id"]
            self.mturk_assignment_id = mapping["assignment_id"]
            self.assignment_time_in_seconds = mapping["assignment_time_in_seconds"]
        except IndexError:
            # HIT does not appear to exist
            self.hit_id = None
            self.mturk_assignment_id = None
            self.assignment_time_in_seconds = -1

    def get_mturk_assignment_id(self) -> str:
        """
        Return the MTurk assignment id associated with this unit
        """
        if self.mturk_assignment_id is None:
            self._sync_hit_mapping()
        assert (
            self.mturk_assignment_id is not None
        ), "Only launched HITs have assignment ids"
        return self.mturk_assignment_id

    def get_mturk_hit_id(self) -> str:
        """
        Return the MTurk hit id associated with this unit
        """
        assert self.hit_id is not None, "Only launched HITs have hit ids"
        return self.hit_id

    def get_requester(self) -> "MTurkRequester":
        """Wrapper around regular Requester as this will be MTurkRequesters"""
        if self.__requester is None:
            self.__requester = cast("MTurkRequester", super().get_requester())
        return self.__requester

    # Required Unit functions

    def get_status(self) -> str:
        """Get status for this unit directly from MTurk"""
        if self.db_status in [
            AssignmentState.CREATED,
            AssignmentState.ACCEPTED,
            AssignmentState.EXPIRED,
        ]:
            return self.db_status

        mturk_hit_id = self.get_mturk_hit_id()
        requester = self.get_requester()
        client = self._get_client(requester._requester_name)
        hit = get_hit(client, mturk_hit_id)
        hit_data = hit["HIT"]

        local_status = self.db_status
        external_status = self.db_status

        if hit_data["HITStatus"] == "Assignable":
            external_status = AssignmentState.LAUNCHED
            if hit_data["Expiration"] == datetime(2015, 1, 1):
                external_status = AssignmentState.EXPIRED
        elif hit_data["HITStatus"] == "Unassignable":
            external_status = AssignmentState.ASSIGNED
        elif hit_data["HITStatus"] in ["Reviewable", "Reviewing"]:
            external_status = AssignmentState.COMPLETED
            agent = self.get_assigned_agent()
            if agent is not None:
                agent_status = agent.get_status()
                if agent_status == AgentState.STATUS_APPROVED:
                    external_status = AssignmentState.ACCEPTED
                elif agent_status == AgentState.STATUS_REJECTED:
                    external_status = AssignmentState.REJECTED
        elif hit_data["HITStatus"] == "Disposed":
            external_status = local_status
        else:
            raise Exception(f"Unexpected HIT status {hit_data['HITStatus']}")

        if external_status != local_status:
            self.set_db_status(external_status)

        return external_status

    def launch(self, task_url: str) -> None:
        """Create this HIT on MTurk (making it availalbe) and register the ids in the local db"""
        run_id = self.get_assignment().get_task_run().db_id
        hit_type_id = self.datastore.get_run(run_id)["hit_type_id"]
        requester = self.get_requester()
        client = self._get_client(requester._requester_name)
        # TODO we need to pull the config file from somewhere
        frame_height = 650
        hit_link, hit_id, response = create_hit_with_hit_type(
            client, frame_height, task_url, hit_type_id
        )
        self.datastore.new_hit(self.db_id, hit_id, TODO_FILL_DURATION)
        self.hit_id = hit_id
        return None

    def expire(self) -> float:
        """
        Send a request to expire the HIT, and if it's not assigned return,
        otherwise just return the maximum assignment duration
        """
        delay = 0
        if self.get_status() == AssignmentState.ASSIGNED:
            # The assignment is currently being worked on,
            # so we will set the wait time to be the
            # amount of time we granted for working on this assignment
            delay = self.assignment_time_in_seconds
        mturk_hit_id = self.get_mturk_hit_id()
        requester = self.get_requester()
        client = self._get_client(requester._requester_name)
        expire_hit(client, mturk_hit_id)
        return delay

    def is_expired(self) -> bool:
        """
        Determine if this unit is expired as according to the vendor.

        In this case, we keep track of the expiration locally by refreshing
        the hit's status and seeing if we've expired.
        """
        return self.get_status() == AssignmentState.EXPIRED

    @staticmethod
    def new(
        db: "MephistoDB", assignment: "Assignment", index: int, pay_amount: float
    ) -> "Unit":
        """Create a Unit for the given assignment"""
        return MTurkUnit._register_unit(
            db, assignment, index, pay_amount, PROVIDER_TYPE
        )
