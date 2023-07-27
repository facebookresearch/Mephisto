#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from datetime import datetime

from mephisto.data_model.unit import Unit
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.providers.mturk.mturk_utils import (
    expire_hit,
    get_hit,
    create_hit_with_hit_type,
    get_bonuses_for_assignment,
    calculate_mturk_task_fee,
    calculate_mturk_bonus_fee,
    get_assignments_for_hit,
)
from mephisto.abstractions.providers.mturk.provider_type import PROVIDER_TYPE
import time
from typing import List, Optional, Tuple, Mapping, Dict, Any, Type, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.assignment import Assignment
    from mephisto.abstractions.providers.mturk.mturk_agent import MTurkAgent
    from mephisto.abstractions.providers.mturk.mturk_requester import MTurkRequester
    from mephisto.abstractions.providers.mturk.mturk_datastore import MTurkDatastore

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


class MTurkUnit(Unit):
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment. It is the smallest 'unit' of work to complete
    the assignment, and this class is only responsible for checking
    the status of that work itself being done.
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "MTurkDatastore" = self.db.get_datastore_for_provider(
            self.PROVIDER_TYPE
        )
        self.hit_id: Optional[str] = None
        self._last_sync_time = 0.0
        self._sync_hit_mapping()
        self.__requester: Optional["MTurkRequester"] = None

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    def _sync_hit_mapping(self) -> None:
        """Sync with the datastore to see if any mappings have updated"""
        if self.datastore.is_hit_mapping_in_sync(self.db_id, self._last_sync_time):
            return
        try:
            mapping = dict(self.datastore.get_hit_mapping(self.db_id))
            self.hit_id = mapping["hit_id"]
            self.mturk_assignment_id = mapping.get("assignment_id")
            self.assignment_time_in_seconds = mapping.get("assignment_time_in_seconds")
        except IndexError:
            # HIT does not appear to exist
            self.hit_id = None
            self.mturk_assignment_id = None
            self.assignment_time_in_seconds = -1
        # We update to a time slightly earlier than now, in order
        # to reduce the risk of a race condition caching an old
        # value the moment it's registered
        self._last_sync_time = time.monotonic() - 1

    def register_from_provider_data(
        self, hit_id: str, mturk_assignment_id: str
    ) -> None:
        """Update the datastore and local information from this registration"""
        self.datastore.register_assignment_to_hit(
            hit_id, self.db_id, mturk_assignment_id
        )
        self._sync_hit_mapping()

    def get_mturk_assignment_id(self) -> Optional[str]:
        """
        Return the MTurk assignment id associated with this unit
        """
        self._sync_hit_mapping()
        return self.mturk_assignment_id

    def get_mturk_hit_id(self) -> Optional[str]:
        """
        Return the MTurk hit id associated with this unit
        """
        self._sync_hit_mapping()
        return self.hit_id

    def get_requester(self) -> "MTurkRequester":
        """Wrapper around regular Requester as this will be MTurkRequesters"""
        if self.__requester is None:
            self.__requester = cast("MTurkRequester", super().get_requester())
        return self.__requester

    def set_db_status(self, status: str) -> None:
        """
        Set the status reflected in the database for this Unit
        """
        super().set_db_status(status)
        if status == AssignmentState.COMPLETED:
            agent = cast("MTurkAgent", self.get_assigned_agent())
            if agent is not None:
                agent_status = agent.get_status()
                if agent_status == AgentState.STATUS_IN_TASK:
                    # Oh no, MTurk has completed the unit, but we don't have
                    # the data. We need to reconcile
                    logger.warning(
                        f"Unit {self} moved to completed, but the agent didn't... "
                        f"Attempting to reconcile with MTurk directly"
                    )
                    try:
                        hit_id = self.get_mturk_hit_id()
                        assert (
                            hit_id is not None
                        ), f"This unit does not have an ID! {self}"

                        agent.attempt_to_reconcile_submitted_data(hit_id)
                    except Exception as e:
                        logger.warning(
                            f"Was not able to reconcile due to an error, {e}. "
                            f"You may need to reconcile this specific Agent manually "
                            f"after the task is completed. See here for details: "
                            f"https://github.com/facebookresearch/Mephisto/pull/442"
                        )
                elif agent_status == AgentState.STATUS_TIMEOUT:
                    # Oh no, this is also bad. we shouldn't be completing for a timed out agent.
                    logger.warning(
                        "Found a timeout that's trying to be pushed to completed with a timed out agent"
                    )
                    pass
            else:
                logger.warning(f"No agent found for completed unit {self}...")

    def clear_assigned_agent(self) -> None:
        """
        Additionally to clearing the agent, we also need to dissociate the
        hit_id from this unit in the MTurkDatastore
        """
        if self.db_status == AssignmentState.COMPLETED:
            logger.warning(
                f"Clearing an agent when COMPLETED, it's likely a submit happened "
                f"but could not be received by the Mephisto backend. This "
                f"assignment clear is thus being ignored, but this message "
                f"is indicative of some data loss. "
            )
            # TODO(OWN) how can we reconcile missing data here? Marking this agent as
            # COMPLETED will pollute the data, but not marking it means that
            # it will have to be the auto-approve deadline.
            return
        super().clear_assigned_agent()
        mturk_hit_id = self.get_mturk_hit_id()
        if mturk_hit_id is not None:
            self.datastore.clear_hit_from_unit(self.db_id)
            self._sync_hit_mapping()

        if self.db_status == AssignmentState.ASSIGNED:
            self.set_db_status(AssignmentState.LAUNCHED)

    def get_pay_amount(self) -> float:
        """
        Return the amount that this Unit is costing against the budget,
        calculating additional fees as relevant
        """
        requester = self.get_requester()
        client = self._get_client(requester._requester_name)
        task_amount = self.pay_amount
        task_fee = calculate_mturk_task_fee(self.pay_amount)
        bonus_amount = get_bonuses_for_assignment(
            client,
            self.get_mturk_assignment_id(),
        )
        bonus_fee = calculate_mturk_bonus_fee(bonus_amount)
        return task_amount + task_fee + bonus_amount + bonus_fee

    # Required Unit functions

    def get_status(self) -> str:
        """
        Get status for this unit cascading from Agent, to MTurk, to local info
        """
        if self.db_status == AssignmentState.CREATED:
            return super().get_status()
        elif self.db_status in AssignmentState.final_unit():
            # These statuses don't change with a get_status call
            return self.db_status

        # These statuses change when we change an existing agent
        agent = self.get_assigned_agent()
        if agent is None:
            if self.db_status in AssignmentState.completed():
                logger.warning(f"Agent for unit {self} is None")
                return self.db_status
            else:
                # Note, we _may_ be able to query the overall HIT Type to see
                # if there's a mismatch at this stage
                return self.db_status

        agent_status = agent.get_status()
        found_status = AgentState.to_assignment_state(agent_status)
        if found_status != self.db_status:
            self.set_db_status(found_status)
        return self.db_status

    def launch(self, task_url: str) -> None:
        """Create this HIT on MTurk (making it available) and register the ids in the local db"""
        task_run = self.get_assignment().get_task_run()
        duration = task_run.get_task_args().assignment_duration_in_seconds
        task_lifetime_in_seconds = (
            task_run.get_task_args().task_lifetime_in_seconds
            if task_run.get_task_args().task_lifetime_in_seconds
            else 60 * 60 * 24 * 31
        )
        run_id = task_run.db_id
        run_details = self.datastore.get_run(run_id)
        hit_type_id = run_details["hit_type_id"]
        requester = self.get_requester()
        client = self._get_client(requester._requester_name)
        frame_height = run_details["frame_height"]
        hit_link, hit_id, response = create_hit_with_hit_type(
            client,
            frame_height,
            task_url,
            hit_type_id,
            lifetime_in_seconds=task_lifetime_in_seconds,
        )
        # TODO(OWN) get this link to the mephisto frontend
        print(hit_link)

        # We create a hit for this unit, but note that this unit may not
        # necessarily match with the same HIT that was launched for it.
        self.datastore.new_hit(hit_id, hit_link, duration, run_id)
        self.set_db_status(AssignmentState.LAUNCHED)
        return None

    def expire(self) -> float:
        """
        Send a request to expire the HIT, and if it's not assigned return,
        otherwise just return the maximum assignment duration
        """
        delay = 0
        status = self.get_status()
        if status in [AssignmentState.EXPIRED, AssignmentState.COMPLETED]:
            return delay
        if status == AssignmentState.ASSIGNED:
            # The assignment is currently being worked on,
            # so we will set the wait time to be the
            # amount of time we granted for working on this assignment
            if self.assignment_time_in_seconds is not None:
                delay = self.assignment_time_in_seconds
            logger.debug(f"Expiring a unit that is ASSIGNED after delay {delay}")
        mturk_hit_id = self.get_mturk_hit_id()
        requester = self.get_requester()
        client = self._get_client(requester._requester_name)
        if mturk_hit_id is not None:
            expire_hit(client, mturk_hit_id)
            return delay
        else:
            unassigned_hit_ids = self.datastore.get_unassigned_hit_ids(self.task_run_id)

            if len(unassigned_hit_ids) == 0:
                self.set_db_status(AssignmentState.EXPIRED)
                return delay
            hit_id = unassigned_hit_ids[0]
            expire_hit(client, hit_id)
            self.datastore.register_assignment_to_hit(hit_id, self.db_id)
            self.set_db_status(AssignmentState.EXPIRED)
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id}, {self.get_mturk_hit_id()}, {self.db_status})"
