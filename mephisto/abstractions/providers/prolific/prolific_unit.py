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
        self.__requester: Optional['ProlificRequester'] = None

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client for usage with `prolific_utils`"""
        return self.datastore.get_client_for_requester(requester_name)

    @property
    def log_prefix(self) -> str:
        return f'[Unit {self.db_id}] '

    def _sync_study_mapping(self) -> None:
        """Sync with the datastore to see if any mappings have updated"""
        if self.datastore.is_study_mapping_in_sync(self.db_id, self._last_sync_time):
            return
        try:
            mapping = dict(self.datastore.get_study_mapping(self.db_id))
            self.prolific_study_id = mapping['prolific_study_id']
            self.prolific_submission_id = mapping.get('prolific_submission_id')
            self.assignment_time_in_seconds = mapping.get('assignment_time_in_seconds')
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
        self, prolific_study_id: str, prolific_submission_id: str,
    ) -> None:
        """Update the datastore and local information from this registration"""
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

    def get_requester(self) -> 'ProlificRequester':
        """Wrapper around regular Requester as this will be ProlificRequester"""
        if self.__requester is None:
            self.__requester = cast('ProlificRequester', super().get_requester())
        return self.__requester

    def get_status(self) -> str:
        """Get status for this unit directly from Prolific, fall back on local info"""

        # -------------------------------------------------------------------------
        # TODO (#1008): Fix this logic. It looked abstract and unclear in Mturk code.
        if self.db_status == AssignmentState.CREATED:
            return super().get_status()
        elif self.db_status in [
            AssignmentState.ACCEPTED,
            AssignmentState.EXPIRED,
            AssignmentState.SOFT_REJECTED,
        ]:
            # These statuses don't change with a get_status call
            return self.db_status

        # -------------------------------------------------------------------------
        # TODO (#1008): Fix this logic. It looked abstract and unclear in Mturk code.
        if self.db_status in [AssignmentState.COMPLETED, AssignmentState.REJECTED]:
            # These statuses only change on agent dependent changes
            agent = self.get_assigned_agent()
            found_status = self.db_status

            if agent is not None:
                agent_status = agent.get_status()
                if agent_status == AgentState.STATUS_APPROVED:
                    found_status = AssignmentState.ACCEPTED
                elif agent_status == AgentState.STATUS_REJECTED:
                    found_status = AssignmentState.REJECTED
                elif agent_status == AgentState.STATUS_SOFT_REJECTED:
                    found_status = AssignmentState.SOFT_REJECTED
            else:
                logger.warning(f'Agent for unit {self} is None')

            if found_status != self.db_status:
                self.set_db_status(found_status)

            return self.db_status

        # Remaining statuses are tracking a live Study
        prolific_study_id = self.get_prolific_study_id()
        if prolific_study_id is None:
            # If the study_id is None and there's an agent still assigned,
            # then that agent has timed out, and we should expire
            agent = self.get_assigned_agent()
            if agent is not None:
                if agent.get_status() != AgentState.STATUS_EXPIRED:
                    agent.update_status(AgentState.STATUS_EXPIRED)

            # Can't determine anything else if there is no Study on this unit
            return self.db_status

        requester: 'ProlificRequester' = self.get_requester()
        client = self._get_client(requester.requester_name)

        # time.sleep(2)  # Prolific servers may take time to bring their data up-to-date
        study = prolific_utils.get_study(client, prolific_study_id)

        if study is None:
            return AssignmentState.EXPIRED

        # Record latest study status from Prolific
        self.datastore.update_study_status(study.id, study.status)

        local_status = self.db_status
        external_status = self.db_status

        if prolific_utils.is_study_expired(study):
            external_status = AssignmentState.EXPIRED
        elif study.status == StudyStatus.UNPUBLISHED:
            external_status = AssignmentState.COMPLETED
        elif study.status == StudyStatus.ACTIVE:
            if self.worker_id is None:
                # Check for NULL worker_id to prevent accidental reversal of unit's progress
                if external_status != AssignmentState.LAUNCHED:
                    logger.debug(
                        f'Moving Unit {self.db_id} status from '
                        f'`{external_status}` to `{AssignmentState.LAUNCHED}`'
                    )
                external_status = AssignmentState.LAUNCHED
        elif study.status == StudyStatus.SCHEDULED:
            # TODO (#1008): Choose correct mapping
            pass
        elif study.status == StudyStatus.PAUSED:
            # TODO (#1008): Choose correct mapping
            pass
        elif study.status == StudyStatus.AWAITING_REVIEW:
            external_status = AssignmentState.COMPLETED
        elif study.status == StudyStatus.COMPLETED:
            external_status = AssignmentState.COMPLETED
        else:
            raise Exception(f'Unexpected Study status {study.status}')

        # -------------------------------------------------------------------------
        # TODO (#1008): Fix this logic. It looked abstract and unclear in Mturk code.
        if external_status != local_status:
            if local_status == AssignmentState.ASSIGNED and external_status in [
                AssignmentState.LAUNCHED,
                AssignmentState.EXPIRED,
            ]:
                # Treat this as a return event, this Study may be doable by someone else
                agent = self.get_assigned_agent()
                agent_status = agent.get_status() if agent else None
                if agent_status in [
                    AgentState.STATUS_ACCEPTED,
                    AgentState.STATUS_IN_TASK,
                    AgentState.STATUS_ONBOARDING,
                    AgentState.STATUS_WAITING,
                    AgentState.STATUS_PARTNER_DISCONNECT,
                ]:
                    # mark the in-task agent as having returned the Study, to
                    # free any running tasks and have Blueprint decide on cleanup.
                    agent.update_status(AgentState.STATUS_RETURNED)
                if external_status == AssignmentState.EXPIRED:
                    # If we're expired, then it won't be doable, and we should update
                    self.set_db_status(external_status)
            else:
                self.set_db_status(external_status)

        return self.db_status

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
        logger.debug(f'{self.log_prefix}Getting pay amount')

        requester = self.get_requester()
        client = self._get_client(requester.requester_name)
        run_args = self.get_task_run().args
        total_amount = prolific_utils.calculate_pay_amount(
            client,
            task_amount=run_args.task.task_reward,
            total_available_places=run_args.provider.prolific_total_available_places,
        )
        logger.debug(f'{self.log_prefix}Pay amount: {total_amount}')

        return total_amount

    def launch(self, task_url: str) -> None:
        """Publish this Study on Prolific (making it available)"""
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
        self.datastore.set_unit_expired(self.db_id, True)
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
        unit = ProlificUnit._register_unit(db, assignment, index, pay_amount, PROVIDER_TYPE)

        # Write unit in provider-specific datastore
        datastore: 'ProlificDatastore' = db.get_datastore_for_provider(PROVIDER_TYPE)
        task_run_details = dict(datastore.get_run(assignment.task_run_id))
        logger.debug(
            f'{ProlificUnit.log_prefix}Create Unit "{unit.db_id}". '
            f'Task Run datastore details: {task_run_details}'
        )
        datastore.create_unit(
            unit_id=unit.db_id,
            run_id=assignment.task_run_id,
            prolific_study_id=task_run_details['prolific_study_id'],
        )
        logger.debug(f'{ProlificUnit.log_prefix}Unit was created in datastore successfully!')

        return unit
