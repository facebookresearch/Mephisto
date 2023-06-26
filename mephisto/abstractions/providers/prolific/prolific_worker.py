#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any
from typing import cast
from typing import List
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING

from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.worker import Worker
from mephisto.utils.logger_core import get_logger

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
    from mephisto.abstractions.providers.prolific.prolific_requester import ProlificRequester
    from mephisto.abstractions.providers.prolific.prolific_unit import ProlificUnit
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit


logger = get_logger(name=__name__)


class ProlificWorker(Worker):
    """
    This class represents an individual - namely a person.
    It maintains components of ongoing identity for a user.
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

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client for usage with `prolific_utils`"""
        return self.datastore.get_client_for_requester(requester_name)

    @property
    def log_prefix(self) -> str:
        return f'[Worker {self.db_id}] '

    def get_prolific_worker_id(self):
        return self.worker_name

    def bonus_worker(
        self, amount: float, reason: str, unit: Optional['Unit'] = None
    ) -> Tuple[bool, str]:
        """Bonus a worker for work any reason. Return success of bonus"""
        logger.debug(f'{self.log_prefix}Paying bonuses')

        if unit is None:
            return False, 'bonusing via compensation tasks not yet available'

        unit: 'ProlificUnit' = cast('ProlificUnit', unit)
        if unit is None:
            # TODO(WISH) soft block from all requesters? Maybe have the main requester soft block?
            return (
                False,
                'Paying bonuses without a unit not yet supported for ProlificWorkers',
            )

        task_run: TaskRun = unit.get_task_run()
        requester = task_run.get_requester()

        client = self._get_client(requester.requester_name)
        task_run_args = task_run.args
        worker_id = self.get_prolific_worker_id()
        study_id = unit.get_prolific_study_id()

        logger.debug(
            f'{self.log_prefix}'
            f'Trying to pay bonuses to worker {worker_id} for Study {study_id}. Amount: {amount}'
        )
        prolific_utils.pay_bonus(
            client,
            task_run_config=task_run_args,
            worker_id=worker_id,
            bonus_amount=amount,
            study_id=study_id,
        )

        logger.debug(f'{self.log_prefix}Bonuses have been paid successfully')

        return True, ''

    @staticmethod
    def _get_first_task_run(requester: 'Requester') -> 'TaskRun':
        task_runs: List[TaskRun] = requester.get_task_runs()
        return task_runs[0]

    def block_worker(
        self,
        reason: str,
        unit: Optional['Unit'] = None,
        requester: Optional['Requester'] = None,
    ) -> Tuple[bool, str]:
        """Block this worker for a specified reason. Return success of block"""
        logger.debug(f'{self.log_prefix}Blocking worker {self.worker_name}')

        if not unit and not requester:
            # TODO(WISH) soft block from all requesters? Maybe have the main requester soft block?
            return (
                False,
                'Blocking without a unit or requester not yet supported for ProlificWorkers',
            )
        elif unit and not requester:
            task_run = unit.get_assignment().get_task_run()
            requester: 'ProlificRequester' = cast('ProlificRequester', task_run.get_requester())
        else:
            task_run = self._get_first_task_run(requester)

        logger.debug(f'{self.log_prefix}Task Run: {task_run}')

        task_run_args = task_run.args
        requester: 'ProlificRequester' = cast('ProlificRequester', requester)
        client = self._get_client(requester.requester_name)
        prolific_utils.block_worker(client, task_run_args, self.worker_name, reason)
        self.datastore.set_worker_blocked(self.worker_name, is_blocked=True)

        logger.debug(f'{self.log_prefix}Worker {self.worker_name} blocked')

        return True, ''

    def unblock_worker(self, reason: str, requester: 'Requester') -> Tuple[bool, str]:
        """Unblock a blocked worker for the specified reason. Return success of unblock"""
        logger.debug(f'{self.log_prefix}Unlocking worker {self.worker_name}')

        task_run = self._get_first_task_run(requester)

        logger.debug(f'{self.log_prefix}Task Run: {task_run}')

        task_run_args = task_run.args
        requester = cast('ProlificRequester', requester)
        client = self._get_client(requester.requester_name)
        prolific_utils.unblock_worker(client, task_run_args, self.worker_name, reason)
        self.datastore.set_worker_blocked(self.worker_name, is_blocked=False)

        logger.debug(f'{self.log_prefix}Worker {self.worker_name} unblocked')

        return True, ''

    def is_blocked(self, requester: 'Requester') -> bool:
        """Determine if a worker is blocked"""
        task_run = self._get_first_task_run(requester)
        task_run_args = task_run.args
        requester = cast('ProlificRequester', requester)
        client = self._get_client(requester.requester_name)
        is_blocked = prolific_utils.is_worker_blocked(client, task_run_args, self.worker_name)

        logger.debug(
            f'{self.log_prefix}'
            f'Worker "{self.worker_name}" {is_blocked=} for Task Run "{task_run.db_id}"'
        )

        return is_blocked

    def is_eligible(self, task_run: 'TaskRun') -> bool:
        """Determine if this worker is eligible for the given task run"""
        return True

    def grant_crowd_qualification(self, qualification_name: str, value: int = 1) -> None:
        """Grant a qualification by the given name to this worker"""
        logger.debug(f'{self.log_prefix}Granting crowd qualification: {qualification_name}')

        p_qualification_details = self.datastore.get_qualification_mapping(qualification_name)

        if p_qualification_details is not None:
            # Use a qualification from DB
            requester = Requester.get(self.db, p_qualification_details['requester_id'])

            assert isinstance(
                requester, ProlificRequester
            ), 'Must be an Prolific requester for Prolific qualifications (participant groups)'

            client = self._get_client(requester.requester_name)
            p_qualification_id = p_qualification_details['prolific_participant_group_id']
        else:
            # Create a new qualification
            target_type = 'prolific'
            requester = self.db.find_requesters(provider_type=target_type)[-1]

            assert isinstance(
                requester, ProlificRequester
            ), '`find_requesters` must return Prolific requester for given provider types'

            task_run = self._get_first_task_run(requester)
            provider_args = task_run.args.provider

            client = self._get_client(requester.requester_name)
            p_workspace = prolific_utils.find_or_create_prolific_workspace(
                client, title=provider_args.prolific_workspace_name,
            )
            p_project = prolific_utils.find_or_create_prolific_project(
                client, p_workspace.id, title=provider_args.prolific_project_name,
            )
            p_qualification_id = requester.create_new_qualification(
                p_project.id, qualification_name,
            )

        p_worker_id = self.get_prolific_worker_id()
        prolific_utils.give_worker_qualification(client, p_worker_id, p_qualification_id)

        logger.debug(
            f'{self.log_prefix}Crowd qualification {qualification_name} has been granted '
            f'for Prolific Participant "{p_worker_id}"'
        )

        return None

    def revoke_crowd_qualification(self, qualification_name: str) -> None:
        """Revoke the qualification by the given name from this worker"""
        logger.debug(f'{self.log_prefix}Revoking crowd qualification: {qualification_name}')

        p_qualification_details = self.datastore.get_qualification_mapping(qualification_name)

        if p_qualification_details is None:
            logger.error(
                f'{self.log_prefix}No locally stored Prolific qualification (participat groups) '
                f'to revoke for name {qualification_name}'
            )
            return None

        requester = Requester.get(self.db, p_qualification_details['requester_id'])

        assert isinstance(
            requester, ProlificRequester
        ), 'Must be an Prolific requester from Prolific qualifications'

        client = self._get_client(requester.requester_name)
        p_worker_id = self.get_prolific_worker_id()
        p_qualification_id = p_qualification_details['prolific_participant_group_id']
        prolific_utils.remove_worker_qualification(client, p_worker_id, p_qualification_id)

        logger.debug(
            f'{self.log_prefix}Crowd qualification {qualification_name} has been revoked '
            f'for Prolific Participant "{p_worker_id}"'
        )

        return None

    @staticmethod
    def new(db: 'MephistoDB', worker_id: str) -> 'Worker':
        new_worker = ProlificWorker._register_worker(db, worker_id, PROVIDER_TYPE)
        # Save worker in provider-specific datastore
        datastore: 'ProlificDatastore' = db.get_datastore_for_provider(PROVIDER_TYPE)
        datastore.ensure_worker_exists(worker_id)
        return new_worker
