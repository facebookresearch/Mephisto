#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from mephisto.abstractions.providers.mturk.provider_type import PROVIDER_TYPE
from mephisto.abstractions.providers.mturk.mturk_datastore import MTurkDatastore
from mephisto.abstractions.crowd_provider import CrowdProvider, ProviderArgs
from mephisto.data_model.requester import RequesterArgs
from mephisto.abstractions.providers.mturk.mturk_agent import MTurkAgent
from mephisto.abstractions.providers.mturk.mturk_requester import MTurkRequester
from mephisto.abstractions.providers.mturk.mturk_unit import MTurkUnit
from mephisto.abstractions.providers.mturk.mturk_worker import MTurkWorker
from mephisto.abstractions.providers.mturk.mturk_utils import (
    create_hit_type,
    create_hit_config,
    delete_qualification,
)
from mephisto.operations.registry import register_mephisto_abstraction
from dataclasses import dataclass, field

from typing import ClassVar, Dict, Any, Optional, Type, List, cast, TYPE_CHECKING

from mephisto.data_model.requester import Requester

if TYPE_CHECKING:
    from mephisto.abstractions.blueprint import SharedTaskState
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.agent import Agent
    from omegaconf import DictConfig


@dataclass
class MTurkProviderArgs(ProviderArgs):
    """Provider args for an MTurk provider"""

    _provider_type: str = PROVIDER_TYPE


@register_mephisto_abstraction()
class MTurkProvider(CrowdProvider):
    """
    Implementation of a crowdprovider that interfaces with MTurk
    """

    # Ensure inherited methods use this level's provider type
    PROVIDER_TYPE = PROVIDER_TYPE

    UnitClass: ClassVar[Type["Unit"]] = MTurkUnit

    RequesterClass: ClassVar[Type["Requester"]] = MTurkRequester

    WorkerClass: ClassVar[Type["Worker"]] = MTurkWorker

    AgentClass: ClassVar[Type["Agent"]] = MTurkAgent

    ArgsClass = MTurkProviderArgs

    def initialize_provider_datastore(self, storage_path: str) -> Any:
        """
        MTurk itself is the source of truth for most data required to run
        tasks on MTurk. The datastore holds sessions to connect with
        MTurk as well as mappings between MTurk ids and Mephisto ids
        """
        return MTurkDatastore(datastore_root=storage_path)

    def _get_client(self, requester_name: str) -> Any:
        """
        Get an mturk client for usage with mturk_utils
        """
        return self.datastore.get_client_for_requester(requester_name)

    def setup_resources_for_task_run(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedTaskState",
        server_url: str,
    ) -> None:
        """Produce the HIT type for this task run."""
        requester = cast("MTurkRequester", task_run.get_requester())
        session = self.datastore.get_session_for_requester(requester._requester_name)
        task_run_id = task_run.db_id

        # Set up HIT config
        config_dir = os.path.join(self.datastore.datastore_root, task_run_id)
        task_args = args.task

        # Find or create relevant qualifications
        qualifications = []
        for qualification in shared_state.qualifications:
            applicable_providers = qualification["applicable_providers"]
            if (
                applicable_providers is None
                or self.PROVIDER_TYPE in applicable_providers
            ):
                qualifications.append(qualification)
        for qualification in qualifications:
            qualification_name = qualification["qualification_name"]
            if requester.PROVIDER_TYPE == "mturk_sandbox":
                qualification_name += "_sandbox"
            if self.datastore.get_qualification_mapping(qualification_name) is None:
                qualification[
                    "QualificationTypeId"
                ] = requester._create_new_mturk_qualification(qualification_name)

        if hasattr(shared_state, "mturk_specific_qualifications"):
            # TODO(OWN) standardize provider-specific qualifications
            qualifications += shared_state.mturk_specific_qualifications  # type: ignore

        # Set up HIT type
        client = self._get_client(requester._requester_name)
        hit_type_id = create_hit_type(client, task_args, qualifications)
        frame_height = (
            task_run.get_blueprint().get_frontend_args().get("frame_height", 0)
        )
        self.datastore.register_run(task_run_id, hit_type_id, config_dir, frame_height)

    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """No cleanup necessary for task type"""
        pass

    @classmethod
    def get_wrapper_js_path(cls):
        """
        Return the path to the `wrap_crowd_source.js` file for this
        provider to be deployed to the server
        """
        return os.path.join(os.path.dirname(__file__), "wrap_crowd_source.js")

    def cleanup_qualification(self, qualification_name: str) -> None:
        """Remove the qualification from the sandbox server, if it exists"""
        mapping = self.datastore.get_qualification_mapping(qualification_name)
        if mapping is None:
            return None

        requester_id = mapping["requester_id"]
        requester = Requester.get(self.db, requester_id)
        assert isinstance(requester, MTurkRequester), "Must be an mturk requester"
        client = requester._get_client(requester._requester_name)
        delete_qualification(client, mapping["mturk_qualification_id"])
