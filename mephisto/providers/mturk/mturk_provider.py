#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from mephisto.data_model.task_config import TaskConfig
from mephisto.providers.mturk.provider_type import PROVIDER_TYPE
from mephisto.providers.mturk.mturk_datastore import MTurkDatastore
from mephisto.data_model.crowd_provider import CrowdProvider
from mephisto.providers.mturk.mturk_agent import MTurkAgent
from mephisto.providers.mturk.mturk_requester import MTurkRequester
from mephisto.providers.mturk.mturk_unit import MTurkUnit
from mephisto.providers.mturk.mturk_worker import MTurkWorker
from mephisto.providers.mturk.mturk_utils import (
    create_hit_type,
    create_hit_config,
    setup_sns_topic,
    delete_sns_topic,
)

from typing import ClassVar, Dict, Any, Optional, Type, List, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.assignment import Unit
    from mephisto.data_model.worker import Worker
    from mephisto.data_model.requester import Requester
    from mephisto.data_model.agent import Agent


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

    SUPPORTED_TASK_TYPES: ClassVar[List[str]] = [
        # TODO
    ]

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
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """
        Set up SNS queue to recieve agent events from MTurk, and produce the
        HIT type for this task run.
        """
        requester = cast("MTurkRequester", task_run.get_requester())
        session = self.datastore.get_session_for_requester(requester._requester_name)
        task_config = task_run.get_task_config()

        # Set up SNS queue
        task_run_id = task_run.db_id
        # task_name = task_run.get_task().task_name
        # arn_id = setup_sns_topic(session, task_name, server_url, task_run_id)
        arn_id = "TEST"

        # Set up HIT config
        # TODO refactor these opts into something gettable elsewhere?
        # TODO these might actually be more relevant to task type
        # and the frontend deployed based on task type
        config_dir = os.path.join(self.datastore.datastore_root, task_run_id)
        # os.mkdirs(config_dir, exist_ok=True)
        # opt = {
        #     'frame_height': 650,
        #     'allow_reviews': False,
        #     'block_mobile': True,
        #     'template_type': 'default',
        #     'run_dir': config_dir,
        # }
        # create_hit_config(opt, task_config, self.is_sandbox())
        task_config = TaskConfig(task_run)

        # Set up HIT type
        client = self._get_client(requester._requester_name)
        hit_type_id = create_hit_type(client, task_config)
        self.datastore.register_run(task_run_id, arn_id, hit_type_id, config_dir)

    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """Shut down the SNS queue for this task."""
        requester = cast("MTurkRequester", task_run.get_requester())
        session = self.datastore.get_session_for_requester(requester._requester_name)
        run_row = self.datastore.get_run(task_run.db_id)
        delete_sns_topic(session, run_row["arn_id"])
