#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from typing import Any
from typing import cast
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
    from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
    from mephisto.data_model.assignment import Assignment

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


class ProlificUnit(Unit):
    """
    This class tracks the status of an individual worker's contribution to a
    higher level assignment. It is the smallest 'unit' of work to complete
    the assignment, and this class is only responsible for checking
    the status of that work itself being done.

    It should be extended for usage with a specific crowd provider
    """

    def __init__(
        self,
        db: 'MephistoDB',
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: 'ProlificDatastore' = db.get_datastore_for_provider(PROVIDER_TYPE)
        self._last_sync_time = 0.0
        self._sync_study_mapping()

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client for usage with `prolific_utils`"""
        return self.datastore.get_client_for_requester(requester_name)

    def _sync_study_mapping(self) -> None:
        """Sync with the datastore to see if any mappings have updated"""
        if self.datastore.is_study_mapping_in_sync(self.db_id, self._last_sync_time):
            return
        try:
            mapping = dict(self.datastore.get_study_mapping(self.db_id))
            self.prolific_study_id = mapping['study_id']
            self.prolific_submission_id = mapping.get('assignment_id')  # TODO (#1008)
            self.assignment_time_in_seconds = mapping.get('assignment_time_in_seconds')
        except IndexError:
            # HIT does not appear to exist
            self.prolific_study_id = None
            self.prolific_submission_id = None  # TODO (#1008)
            self.assignment_time_in_seconds = -1
        # We update to a time slightly earlier than now, in order
        # to reduce the risk of a race condition caching an old
        # value the moment it's registered
        self._last_sync_time = time.monotonic() - 1

    def register_from_provider_data(self, hit_id: str, mturk_assignment_id: str) -> None:
        """Update the datastore and local information from this registration"""
        # TODO (#1008): I'm not sure whether we need this for Prolific
        return None

    def get_prolific_submission_id(self) -> Optional[str]:
        """
        Return the Prolific assignment id associated with this unit
        """
        # TODO (#1008): I'm not sure whether we need this for Prolific
        return None

    def get_prolific_study_id(self) -> Optional[str]:
        """
        Return the Porlific Study ID associated with this unit
        """
        self._sync_study_mapping()
        return self.prolific_study_id

    def get_requester(self) -> 'ProlificRequester':
        """Wrapper around regular Requester as this will be ProlificRequester"""
        if self.__requester is None:
            self.__requester = cast('ProlificRequester', super().get_requester())
        return self.__requester

    def clear_assigned_agent(self) -> None:
        """
        Additionally to clearing the agent, we also need to dissociate the
        study_id from this unit in the ProlificDatastore
        """
        if self.db_status == AssignmentState.COMPLETED:
            logger.warning(
                f"Clearing an agent when COMPLETED, it's likely a submit happened "
                f"but could not be received by the Mephisto backend. This "
                f"assignment clear is thus being ignored, but this message "
                f"is indicative of some data loss."
            )
            # TODO(OWN) how can we reconcile missing data here? Marking this agent as
            #  COMPLETED will pollute the data, but not marking it means that
            #  it will have to be the auto-approve deadline.
            return

        super().clear_assigned_agent()

        prolific_study_id = self.get_prolific_study_id()
        if prolific_study_id is not None:
            self.datastore.clear_study_from_unit(unit_id=self.db_id)
            self._sync_study_mapping()

        if self.db_status == AssignmentState.ASSIGNED:
            self.set_db_status(AssignmentState.LAUNCHED)

    def get_pay_amount(self) -> float:
        """
        Return the amount that this Unit is costing against the budget,
        calculating additional fees as relevant
        """
        requester = self.get_requester()
        client = self._get_client(requester.requester_name)
        run_args = self.get_task_run().args
        total_amount = prolific_utils.calculate_pay_amount(
            client,
            task_amount=run_args.task.task_reward,
            total_available_places=run_args.provider.prolific_total_available_places,
        )
        return total_amount

    def launch(self, task_url: str) -> None:
        """Publish this Study on Prolific (making it available)"""
        requester = self.get_requester()
        client = self._get_client(requester.requester_name)
        prolific_study_id = self.get_prolific_study_id()
        prolific_utils.publish_study(client, prolific_study_id)
        self.set_db_status(AssignmentState.LAUNCHED)
        return None

    def expire(self) -> float:
        """Send a request to expire the study"""
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
            logger.debug(f'Expiring a unit that is ASSIGNED after delay {delay}')

        prolific_study_id = self.get_prolific_study_id()
        requester = self.get_requester()
        client = self._get_client(requester.requester_name)
        if prolific_study_id is not None:
            prolific_utils.expire_study(client, prolific_study_id)
            return delay
        else:
            unassigned_study_ids = self.datastore.get_unassigned_study_ids(self.task_run_id)

            if len(unassigned_study_ids) == 0:
                self.set_db_status(AssignmentState.EXPIRED)
                return delay

            prolific_study_id = unassigned_study_ids[0]
            prolific_utils.expire_study(client, prolific_study_id)
            # TODO (#1008): We do not need that if we don't have assignments in Prolific (???)
            # self.datastore.register_assignment_to_hit(study_id, self.db_id)
            self.set_db_status(AssignmentState.EXPIRED)
            return delay

    def is_expired(self) -> bool:
        """
        Determine if this unit is expired as according to the vendor.

        In this case, we keep track of the expiration locally by refreshing
        the study's status and seeing if we've expired.
        """
        return self.get_status() == AssignmentState.EXPIRED

    @staticmethod
    def new(
        db: 'MephistoDB', assignment: 'Assignment', index: int, pay_amount: float
    ) -> 'Unit':
        """Create a Unit for the given assignment"""
        return ProlificUnit._register_unit(db, assignment, index, pay_amount, PROVIDER_TYPE)
