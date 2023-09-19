#!/usr/bin/env python3
import json

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

from omegaconf import DictConfig

from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.api.client import ProlificClient
from mephisto.abstractions.providers.prolific.provider_type import PROVIDER_TYPE
from mephisto.data_model.worker import Worker
from mephisto.utils.logger_core import get_logger
from mephisto.utils.qualifications import worker_is_qualified

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
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "ProlificDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client for usage with `prolific_utils`"""
        return self.datastore.get_client_for_requester(requester_name)

    @property
    def log_prefix(self) -> str:
        return f"[Worker {self.db_id}] "

    def get_prolific_participant_id(self):
        return self.worker_name

    def bonus_worker(
        self, amount: float, reason: str, unit: Optional["Unit"] = None
    ) -> Tuple[bool, str]:
        """Bonus a worker for work any reason. Return success of bonus"""
        logger.debug(f"{self.log_prefix}Paying bonuses")

        if unit is None:
            return False, "bonusing via compensation tasks not yet available"

        unit: "ProlificUnit" = cast("ProlificUnit", unit)
        if unit is None:
            # TODO(WISH) soft block from all requesters? Maybe have the main requester soft block?
            return (
                False,
                "Paying bonuses without a unit not yet supported for ProlificWorkers",
            )

        task_run: TaskRun = unit.get_task_run()
        requester = task_run.get_requester()

        client = self._get_client(requester.requester_name)
        task_run_args = task_run.args
        participant_id = self.get_prolific_participant_id()
        study_id = unit.get_prolific_study_id()

        logger.debug(
            f"{self.log_prefix}"
            f"Trying to pay bonuses to worker {participant_id} for Study {study_id}. "
            f"Amount: {amount}"
        )
        prolific_utils.pay_bonus(
            client,
            task_run_config=task_run_args,
            worker_id=participant_id,
            bonus_amount=amount,
            study_id=study_id,
        )

        logger.debug(f"{self.log_prefix}Bonuses have been paid successfully")

        return True, ""

    @staticmethod
    def _get_first_task_run(requester: "Requester") -> "TaskRun":
        task_runs: List[TaskRun] = requester.get_task_runs()
        return task_runs[0]

    def block_worker(
        self,
        reason: str,
        unit: Optional["Unit"] = None,
        requester: Optional["Requester"] = None,
    ) -> Tuple[bool, str]:
        """Block this worker for a specified reason. Return success of block"""
        logger.debug(f"{self.log_prefix}Blocking worker {self.worker_name}")

        if not unit and not requester:
            # TODO(WISH) soft block from all requesters? Maybe have the main requester soft block?
            return (
                False,
                "Blocking without a unit or requester not yet supported for ProlificWorkers",
            )
        elif unit and not requester:
            task_run = unit.get_assignment().get_task_run()
            requester: "ProlificRequester" = cast("ProlificRequester", task_run.get_requester())
        else:
            task_run = self._get_first_task_run(requester)

        logger.debug(f"{self.log_prefix}Task Run: {task_run}")

        task_run_args = task_run.args
        requester: "ProlificRequester" = cast("ProlificRequester", requester)
        client = self._get_client(requester.requester_name)
        prolific_utils.block_worker(client, task_run_args, self.worker_name, reason)
        self.datastore.set_worker_blocked(self.worker_name, is_blocked=True)

        # Find all previously granted qualifications for this worker,
        # and remove the worker from all related Prolific Participant Groups
        db_granted_qualifications = self.db.find_granted_qualifications(worker_id=self.db_id)
        if db_granted_qualifications:
            db_qualification_ids = [q.qualification_id for q in db_granted_qualifications]
            prolific_qualifications = self.datastore.find_qualifications_for_running_studies(
                db_qualification_ids,
            )
            prolific_participant_group_ids = [
                p["prolific_participant_group_id"] for p in prolific_qualifications
            ]
            for prolific_participant_group_id in prolific_participant_group_ids:
                prolific_utils.remove_worker_qualification(
                    client,
                    self.worker_name,
                    prolific_participant_group_id,
                )

        logger.debug(f"{self.log_prefix}Worker {self.worker_name} blocked")

        return True, ""

    def unblock_worker(self, reason: str, requester: "Requester") -> Tuple[bool, str]:
        """Unblock a blocked worker for the specified reason. Return success of unblock"""
        logger.debug(f"{self.log_prefix}Unlocking worker {self.worker_name}")

        task_run = self._get_first_task_run(requester)

        logger.debug(f"{self.log_prefix}Task Run: {task_run}")

        task_run_args = task_run.args
        requester = cast("ProlificRequester", requester)
        client = self._get_client(requester.requester_name)
        prolific_utils.unblock_worker(client, task_run_args, self.worker_name, reason)
        self.datastore.set_worker_blocked(self.worker_name, is_blocked=False)

        # Include unblocked Worker into all Participant Groups for currently running Studies,
        # if he is qualified at the moment
        self._grant_crowd_qualifications(client)
        logger.debug(f"{self.log_prefix}Worker {self.worker_name} unblocked")

        return True, ""

    def is_blocked(self, requester: "Requester") -> bool:
        """Determine if a worker is blocked"""
        task_run = self._get_first_task_run(requester)
        requester = cast("ProlificRequester", requester)
        is_blocked = self.datastore.get_worker_blocked(self.get_prolific_participant_id())

        logger.debug(
            f"{self.log_prefix}"
            f'Worker "{self.worker_name}" {is_blocked=} for Task Run "{task_run.db_id}"'
        )

        return is_blocked

    def is_eligible(self, task_run: "TaskRun") -> bool:
        """Determine if this worker is eligible for the given task run"""
        return True

    def _grant_crowd_qualifications(
        self,
        client: ProlificClient,
        qualification_name: Optional[str] = None,
    ) -> None:
        """
        Grant specified qualification if `qualification_name` is passed or
        all previously granted to the current Worker, and he is qualified at the moment
        """
        prolific_participant_id = self.get_prolific_participant_id()
        is_blocked = self.datastore.get_worker_blocked(prolific_participant_id)
        if is_blocked:
            logger.debug(
                f"{self.log_prefix}"
                f'Worker is blocked. Cannot grant qualification "{qualification_name}"'
            )
            return None

        db_qualifications = self.db.find_qualifications(qualification_name)

        if db_qualifications:
            # If we found already created qualifications in Mephisto
            db_qualification_ids = [q.db_id for q in db_qualifications]
            prolific_qualifications = self.datastore.find_qualifications_for_running_studies(
                db_qualification_ids,
            )
            qualifications_groups = [
                (json.loads(i["json_qual_logic"]), i["prolific_participant_group_id"])
                for i in prolific_qualifications
            ]

            for qualifications, prolific_participant_group_id in qualifications_groups:
                if worker_is_qualified(self, qualifications):
                    # Worker is still qualified or was upgraded, and so is eligible now
                    prolific_utils.give_worker_qualification(
                        client,
                        self.worker_name,
                        prolific_participant_group_id,
                    )
                else:
                    # Worker is now not eligible for this Participant Group anymore
                    prolific_utils.remove_worker_qualification(
                        client,
                        self.worker_name,
                        prolific_participant_group_id,
                    )

        logger.debug(
            f"{self.log_prefix}Crowd qualification {qualification_name} has been granted "
            f'for Prolific Participant "{prolific_participant_id}"'
        )

    def grant_crowd_qualification(
        self,
        qualification_name: Optional[str] = None,
        value: int = 1,
    ) -> None:
        """Grant qualification by the given name to this worker"""
        logger.debug(f"{self.log_prefix}Granting crowd qualification: {qualification_name}")

        requester = cast(
            "ProlificRequester",
            self.db.find_requesters(provider_type=self.provider_type)[-1],
        )
        client = self._get_client(requester.requester_name)

        self._grant_crowd_qualifications(client, qualification_name)
        return None

    def revoke_crowd_qualification(self, qualification_name: str) -> None:
        """Revoke qualification by given name from this worker"""
        logger.debug(f"{self.log_prefix}Revoking crowd qualification: {qualification_name}")

        p_qualification_details = self.datastore.get_qualification_mapping(qualification_name)

        if p_qualification_details is None:
            logger.error(
                f"{self.log_prefix}No locally stored Prolific qualification (Participant Groups) "
                f"to revoke for name {qualification_name}"
            )
            return None

        requester = Requester.get(self.db, p_qualification_details["requester_id"])

        assert isinstance(
            requester, ProlificRequester
        ), "Must be an Prolific requester from Prolific qualifications"

        client = self._get_client(requester.requester_name)
        p_worker_id = self.get_prolific_participant_id()
        p_qualification_id = p_qualification_details["prolific_participant_group_id"]
        prolific_utils.remove_worker_qualification(client, p_worker_id, p_qualification_id)

        logger.debug(
            f"{self.log_prefix}Crowd qualification {qualification_name} has been revoked "
            f'for Prolific Participant "{p_worker_id}"'
        )

        return None

    @staticmethod
    def new(db: "MephistoDB", worker_id: str) -> "Worker":
        new_worker = ProlificWorker._register_worker(db, worker_id, PROVIDER_TYPE)
        # Save worker in provider-specific datastore
        datastore: "ProlificDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)
        datastore.ensure_worker_exists(worker_id)
        return new_worker
