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

from mephisto.abstractions._subcomponents.agent_state import AgentState
from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.api.constants import SubmissionStatus
from mephisto.abstractions.providers.prolific.api.constants import StudyStatus
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.unit import Unit

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
    from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
    from mephisto.data_model.assignment import Assignment

from mephisto.utils.logger_core import get_logger

SUBMISSION_STATUS_TO_ASSIGNMENT_STATE_MAP = {
    SubmissionStatus.RESERVED: AssignmentState.CREATED,
    SubmissionStatus.TIMED_OUT: AssignmentState.EXPIRED,
    SubmissionStatus.AWAITING_REVIEW: AssignmentState.COMPLETED,
    SubmissionStatus.APPROVED: AssignmentState.COMPLETED,
    SubmissionStatus.RETURNED: AssignmentState.COMPLETED,
    SubmissionStatus.REJECTED: AssignmentState.REJECTED,
}

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
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "ProlificDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)
        self._last_sync_time = 0.0
        self._sync_study_mapping()
        self.__requester: Optional["ProlificRequester"] = None

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client for usage with `prolific_utils`"""
        return self.datastore.get_client_for_requester(requester_name)

    @property
    def log_prefix(self) -> str:
        return f"[Unit {self.db_id}] "

    def _sync_study_mapping(self) -> None:
        """Sync with the datastore to see if any mappings have updated"""
        if self.datastore.is_study_mapping_in_sync(self.db_id, self._last_sync_time):
            return
        try:
            mapping = dict(self.datastore.get_study_mapping(self.db_id))
            self.prolific_study_id = mapping["prolific_study_id"]
            self.prolific_submission_id = mapping.get("prolific_submission_id")
            self.assignment_time_in_seconds = mapping.get("assignment_time_in_seconds")
        except IndexError:
            # Study does not appear to exist
            self.prolific_study_id = None
            self.prolific_submission_id = None
            self.assignment_time_in_seconds = -1
        # We update to a time slightly earlier than now, in order
        # to reduce the risk of a race condition caching an old
        # value the moment it's registered
        self._last_sync_time = time.monotonic() - 1

    def register_from_provider_data(
        self,
        prolific_study_id: str,
        prolific_submission_id: str,
    ) -> None:
        """Update the datastore and local information from this registration"""
        self.datastore.set_submission_for_unit(
            unit_id=self.db_id,
            prolific_submission_id=prolific_submission_id,
        )
        self.datastore.register_submission_to_study(
            prolific_study_id=prolific_study_id,
            unit_id=self.db_id,
            prolific_submission_id=prolific_submission_id,
        )
        self._sync_study_mapping()

    def get_prolific_submission_id(self) -> Optional[str]:
        """Return the Prolific Submission ID (assignment ID) associated with this unit"""
        self._sync_study_mapping()
        return self.prolific_submission_id

    def get_prolific_study_id(self) -> Optional[str]:
        """Return the Porlific Study ID associated with this unit"""
        self._sync_study_mapping()
        return self.prolific_study_id

    def get_requester(self) -> "ProlificRequester":
        """Wrapper around regular Requester as this will be ProlificRequester"""
        if self.__requester is None:
            self.__requester = cast("ProlificRequester", super().get_requester())
        return self.__requester

    def get_status(self) -> str:
        """Get status for this unit directly from Prolific, fall back on local info"""

        if self.db_status == AssignmentState.CREATED:
            return super().get_status()
        elif self.db_status in AssignmentState.final_unit():
            # These statuses don't change with a get_status call
            return self.db_status

        # These statuses change when we change an existing agent
        agent = self.get_assigned_agent()
        if agent is None:
            if self.db_status in AssignmentState.completed():
                logger.warning(f"Agent for completed unit {self} is None")

            return self.db_status

        # Get API client
        requester: "ProlificRequester" = self.get_requester()
        client = self._get_client(requester.requester_name)

        # time.sleep(2)  # Prolific servers may take time to bring their data up-to-date

        # Get Study from Prolific, record status
        study = prolific_utils.get_study(client, self.get_prolific_study_id())
        if study is None:
            return AssignmentState.EXPIRED
        self.datastore.update_study_status(study.id, study.status)
        study_is_completed = study.status in [
            StudyStatus.COMPLETED,
            StudyStatus.AWAITING_REVIEW,
        ]

        # Get Submission from Prolific, record status
        datastore_unit = self.datastore.get_unit(self.db_id)
        prolific_submission_id = datastore_unit["prolific_submission_id"]
        prolific_submission = None
        if prolific_submission_id:
            prolific_submission = prolific_utils.get_submission(client, prolific_submission_id)
            self.datastore.update_submission_status(
                prolific_submission_id,
                prolific_submission.status,
            )

        # Check Unit status
        local_status = self.db_status
        external_status = self.db_status

        if study_is_completed:
            # Note: Prolific cannot expire a study while there are incomplete Submissions
            # so we always expire the unit here (without checking for Submissions status).

            # Checking for NULL worker_id to avoid labeling not-yet-worked-on units as "COMPLETED"
            if self.worker_id is None:
                external_status = AssignmentState.EXPIRED
            else:
                external_status = AssignmentState.COMPLETED

        if not study_is_completed and prolific_submission:
            if prolific_submission.status == SubmissionStatus.ACTIVE:
                if self.worker_id is None:
                    # Check for NULL worker_id to prevent accidental reversal of unit's progress
                    if external_status != AssignmentState.LAUNCHED:
                        logger.debug(
                            f"{self.log_prefix}Moving Unit {self.db_id} status from "
                            f"`{external_status}` to `{AssignmentState.LAUNCHED}`"
                        )
                    external_status = AssignmentState.LAUNCHED
            elif prolific_submission.status == SubmissionStatus.PROCESSING:
                # This is just Prolific's transient status to move Submission between 2 statuses
                pass
            else:
                external_status = SUBMISSION_STATUS_TO_ASSIGNMENT_STATE_MAP.get(
                    prolific_submission.status,
                )
                if not external_status:
                    raise Exception(f"Unexpected Submission status {prolific_submission.status}")

        if external_status != local_status:
            self.set_db_status(external_status)

        return self.db_status

    def set_db_status(self, status: str) -> None:
        super().set_db_status(status)

        if status in AssignmentState.completed():
            # Decrement available places in datastore if status is in completed statuses
            logger.debug(
                f"{self.log_prefix}Decrementing `actual_available_places` and "
                f"`listed_available_places`, because unit `{self.db_id}` is completed."
            )
            task_run_id = self.get_task_run().db_id
            datastore_task_run = self.datastore.get_run(task_run_id)
            self.datastore.set_available_places_for_run(
                run_id=task_run_id,
                actual_available_places=datastore_task_run["actual_available_places"] - 1,
                listed_available_places=datastore_task_run["listed_available_places"] - 1,
            )

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

        if self.db_status == AssignmentState.ASSIGNED:
            self.set_db_status(AssignmentState.LAUNCHED)

    def get_pay_amount(self) -> float:
        """
        Return the amount that this Unit is costing against the budget,
        calculating additional fees as relevant
        """
        logger.debug(f"{self.log_prefix}Getting pay amount")

        requester = self.get_requester()
        client = self._get_client(requester.requester_name)
        run_args = self.get_task_run().args
        total_amount = prolific_utils.calculate_pay_amount(
            client,
            task_amount=run_args.task.task_reward,
            # TODO: what value should go in here when we auto-increment `total_available_places`?
            total_available_places=1,
        )
        logger.debug(f"{self.log_prefix}Pay amount: {total_amount}")

        return total_amount

    def launch(self, task_url: str) -> None:
        """Publish this Unit on Prolific (making it available)"""

        # [Depends on Prolific] if we have `max_num_concurrent_units` specified,
        # the Study cannot be stopped from Prolific UI.
        # That's beceause Mephisto waits until "completed" (not "assigned") status of previous
        # units before launching new ones. So if Prolific temporarily runs out of available Units
        # (and `listed_available_places` drops to zero), Prolific will automatically set Study
        # to "AWAITING_REVIEW" status. Therefore, when we receive "AWAITING_REVIEW" status we
        # don't know if it's this situation, or someone just clicked "Stop Study" in Prolific UI.

        # Update available places in provider-specific datastore
        task_run_id = self.get_task_run().db_id
        datastore_task_run = self.datastore.get_run(task_run_id)

        actual_available_places = datastore_task_run["actual_available_places"]
        listed_available_places = datastore_task_run["listed_available_places"]
        provider_increment_needed = False

        if actual_available_places is None:
            # It's the first unit in our Study. So we set available places
            # to match the setup of Prolific Study (which was created with 1 place)
            actual_available_places = 1
            listed_available_places = 1
        elif actual_available_places == listed_available_places:
            actual_available_places += 1
            listed_available_places += 1
            provider_increment_needed = True
        else:
            actual_available_places += 1

        self.datastore.set_available_places_for_run(
            run_id=task_run_id,
            actual_available_places=actual_available_places,
            listed_available_places=listed_available_places,
        )

        # Update `total_available_places` on Prolific
        if provider_increment_needed:
            requester = self.get_requester()
            client = self._get_client(requester.requester_name)
            prolific_utils.increase_total_available_places_for_study(
                client,
                datastore_task_run["prolific_study_id"],
            )

        # Change DB status
        self.set_db_status(AssignmentState.LAUNCHED)

        return None

    def expire(self) -> float:
        """
        Send a request to expire the Prolific Study, and if it's not assigned return 0,
        otherwise just return the maximum assignment duration
        """
        delay = 0
        status = self.get_status()

        # Decrement `actual_available_places` in datastore
        if status == AssignmentState.EXPIRED:
            task_run = self.get_task_run()
            datastore_task_run = self.datastore.get_run(task_run.db_id)

            actual_available_places = datastore_task_run["actual_available_places"]
            listed_available_places = datastore_task_run["listed_available_places"]

            listed_places_decrement = 1 if task_run.get_is_completed() else 0
            self.datastore.set_available_places_for_run(
                run_id=task_run.db_id,
                actual_available_places=actual_available_places - 1,
                listed_available_places=listed_available_places - listed_places_decrement,
            )

            if actual_available_places == 0:
                # If Mephisto has expired all its units, we force-stop Prolific Study
                requester = self.get_requester()
                client = self._get_client(requester.requester_name)
                prolific_utils.stop_study(client, datastore_task_run["prolific_study_id"])

        # Update status
        if status in [AssignmentState.EXPIRED, AssignmentState.COMPLETED]:
            return delay

        if status == AssignmentState.ASSIGNED:
            # The assignment is currently being worked on,
            # so we will set the wait time to be the
            # amount of time we granted for working on this assignment
            if self.assignment_time_in_seconds is not None:
                delay = self.assignment_time_in_seconds
            logger.debug(f"{self.log_prefix}Expiring a unit that is ASSIGNED after delay {delay}")

        prolific_study_id = self.get_prolific_study_id()
        requester = self.get_requester()
        client = self._get_client(requester.requester_name)
        self.datastore.set_unit_expired(self.db_id, True)

        # Operator expires only units (not studies), so we expire study when no active units left
        if self.datastore.all_study_units_are_expired(self.task_run_id):
            prolific_utils.expire_study(client, prolific_study_id)

        return delay

    def is_expired(self) -> bool:
        """
        Determine if this unit is expired as according to the vendor.

        In this case, we keep track of the expiration locally by refreshing
        the study's status and seeing if we've expired.
        """
        return self.get_status() == AssignmentState.EXPIRED

    @staticmethod
    def new(db: "MephistoDB", assignment: "Assignment", index: int, pay_amount: float) -> "Unit":
        """Create a Unit for the given assignment"""
        unit = ProlificUnit._register_unit(db, assignment, index, pay_amount, PROVIDER_TYPE)

        # Write unit in provider-specific datastore
        datastore: "ProlificDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)
        task_run_details = dict(datastore.get_run(assignment.task_run_id))
        logger.debug(
            f'{ProlificUnit.log_prefix}Create Unit "{unit.db_id}". '
            f"Task Run datastore details: {task_run_details}"
        )
        datastore.create_unit(
            unit_id=unit.db_id,
            run_id=assignment.task_run_id,
            prolific_study_id=task_run_details["prolific_study_id"],
        )
        logger.debug(f"{ProlificUnit.log_prefix}Unit was created in datastore successfully!")

        return unit
