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

    def get_prolific_worker_id(self):
        return self.worker_name

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client for usage with `prolific_utils`"""
        return self.datastore.get_client_for_requester(requester_name)

    def bonus_worker(
        self, amount: float, reason: str, unit: Optional['Unit'] = None
    ) -> Tuple[bool, str]:
        """Bonus a worker for work any reason. Return success of bonus"""
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

        prolific_utils.pay_bonus(
            client,
            run_config=task_run_args,
            worker_id=self.get_prolific_worker_id(),
            bonus_amount=amount,
            study_id=unit.get_prolific_study_id(),
        )

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
        if unit is None and requester is None:
            # TODO(WISH) soft block from all requesters? Maybe have the main requester soft block?
            return (
                False,
                'Blocking without a unit or requester not yet supported for ProlificWorkers',
            )
        elif unit is not None and requester is None:
            task_run = unit.get_assignment().get_task_run()

            requester: 'ProlificRequester' = cast('ProlificRequester', task_run.get_requester())
        else:
            task_run = self._get_first_task_run(requester)

        task_run_args = task_run.args
        requester: 'ProlificRequester' = cast('ProlificRequester', requester)
        client = self._get_client(requester.requester_name)
        prolific_utils.block_worker(client, task_run_args, self.worker_name, reason)
        return True, ''

    def unblock_worker(self, reason: str, requester: 'Requester') -> Tuple[bool, str]:
        """Unblock a blocked worker for the specified reason. Return success of unblock"""
        task_run = self._get_first_task_run(requester)
        task_run_args = task_run.args
        requester = cast('ProlificRequester', requester)
        client = self._get_client(requester.requester_name)
        prolific_utils.unblock_worker(client, task_run_args, self.worker_name, reason)
        return True, ''

    def is_blocked(self, requester: 'Requester') -> bool:
        """Determine if a worker is blocked"""
        task_run = self._get_first_task_run(requester)
        task_run_args = task_run.args
        requester = cast('ProlificRequester', requester)
        client = self._get_client(requester.requester_name)
        is_blocked = prolific_utils.is_worker_blocked(client, task_run_args, self.worker_name)
        return is_blocked

    def is_eligible(self, task_run: 'TaskRun') -> bool:
        """Determine if this worker is eligible for the given task run"""
        return True

    def grant_crowd_qualification(self, qualification_name: str, value: int = 1) -> None:
        """Grant a qualification by the given name to this worker"""
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
            p_workspace_id = prolific_utils.find_or_create_prolific_workspace(
                client, title=provider_args.prolific_workspace_name,
            )
            p_project_id = prolific_utils.find_or_create_prolific_project(
                client, p_workspace_id, title=provider_args.prolific_project_name,
            )
            p_qualification_id = requester.create_new_qualification(
                p_project_id, qualification_name,
            )

        p_worker_id = self.get_prolific_worker_id()
        prolific_utils.give_worker_qualification(client, p_worker_id, p_qualification_id)

        return None

    def revoke_crowd_qualification(self, qualification_name: str) -> None:
        """Revoke the qualification by the given name from this worker"""
        p_qualification_details = self.datastore.get_qualification_mapping(qualification_name)

        if p_qualification_details is None:
            logger.error(
                f'No locally stored Prolific qualification (participat groups) '
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

        return None

    @staticmethod
    def new(db: 'MephistoDB', worker_id: str) -> 'Worker':
        return ProlificWorker._register_worker(db, worker_id, PROVIDER_TYPE)
