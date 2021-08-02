#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
import shutil
import os
import tempfile
import time

from typing import List

from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.abstractions.blueprints.mock.mock_task_runner import MockTaskRunner
from mephisto.abstractions.architects.mock_architect import MockArchitect
from mephisto.abstractions.providers.mock.mock_provider import MockProvider
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_singleton_database import MephistoSingletonDB
from mephisto.operations.task_launcher import TaskLauncher
from mephisto.abstractions.test.utils import get_test_task_run
from mephisto.data_model.assignment import InitializationData
from mephisto.data_model.task_run import TaskRun
from mephisto.operations.supervisor import Supervisor, Job
from mephisto.abstractions.blueprint import SharedTaskState


from mephisto.abstractions.architects.mock_architect import (
    MockArchitect,
    MockArchitectArgs,
)
from mephisto.operations.hydra_config import MephistoConfig
from mephisto.abstractions.providers.mock.mock_provider import MockProviderArgs
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprintArgs
from mephisto.data_model.task_config import TaskConfigArgs
from omegaconf import OmegaConf


EMPTY_STATE = SharedTaskState()


class BaseTestSupervisor:
    """
    Unit testing for the Mephisto Supervisor,
    uses WebsocketChannel and MockArchitect
    """

    DB_CLASS = None

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)
        self.task_id = self.db.new_task("test_mock", MockBlueprint.BLUEPRINT_TYPE)
        self.task_run_id = get_test_task_run(self.db)
        self.task_run = TaskRun(self.db, self.task_run_id)

        architect_config = OmegaConf.structured(
            MephistoConfig(architect=MockArchitectArgs(should_run_server=True))
        )

        self.architect = MockArchitect(
            self.db, architect_config, EMPTY_STATE, self.task_run, self.data_dir
        )
        self.architect.prepare()
        self.architect.deploy()
        self.urls = self.architect._get_socket_urls()  # FIXME
        self.url = self.urls[0]
        self.provider = MockProvider(self.db)
        self.provider.setup_resources_for_task_run(
            self.task_run, self.task_run.args, EMPTY_STATE, self.url
        )
        self.launcher = TaskLauncher(
            self.db, self.task_run, self.get_mock_assignment_data_array()
        )
        self.launcher.create_assignments()
        self.launcher.launch_units(self.url)
        self.sup = None

    def tearDown(self):
        if self.sup is not None:
            self.sup.shutdown()
        self.launcher.expire_units()
        self.architect.cleanup()
        self.architect.shutdown()
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def get_mock_assignment_data_array(self) -> List[InitializationData]:
        mock_data = MockTaskRunner.get_mock_assignment_data()
        return [mock_data, mock_data]

    def test_initialize_supervisor(self):
        """Ensure that the supervisor object can even be created"""
        sup = Supervisor(self.db)
        self.assertIsNotNone(sup)
        self.assertDictEqual(sup.agents, {})
        self.assertDictEqual(sup.channels, {})
        sup.shutdown()

    def test_channel_operations(self):
        """
        Initialize a channel, and ensure the basic
        startup and shutdown functions are working
        """
        sup = Supervisor(self.db)
        self.sup = sup
        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        args = MockBlueprint.ArgsClass()
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        task_runner = TaskRunnerClass(self.task_run, config, EMPTY_STATE)
        test_job = Job(
            architect=self.architect,
            task_runner=task_runner,
            provider=self.provider,
            qualifications=[],
            registered_channel_ids=[],
        )

        channels = self.architect.get_channels(
            sup._on_channel_open, sup._on_catastrophic_disconnect, sup._on_message
        )
        channel = channels[0]
        channel.open()
        channel_id = channel.channel_id
        self.assertIsNotNone(channel_id)
        channel.close()
        self.assertTrue(channel.is_closed())

    def test_register_concurrent_job(self):
        """Test registering and running a job that requires multiple workers"""
        # Handle baseline setup
        sup = Supervisor(self.db)
        self.sup = sup
        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        args = MockBlueprint.ArgsClass()
        args.timeout_time = 5
        args.is_concurrent = False
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        task_runner = TaskRunnerClass(self.task_run, config, EMPTY_STATE)
        sup.register_job(self.architect, task_runner, self.provider)
        self.assertEqual(len(sup.channels), 1)
        channel_info = list(sup.channels.values())[0]
        self.assertIsNotNone(channel_info)
        self.assertTrue(channel_info.channel.is_alive)
        channel_id = channel_info.channel_id
        task_runner = channel_info.job.task_runner
        self.assertIsNotNone(channel_id)
        self.assertEqual(
            len(self.architect.server.subs),
            1,
            "MockServer doesn't see registered channel",
        )
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )
        sup.launch_sending_thread()
        self.assertIsNotNone(sup.sending_thread)

        # Register a worker
        mock_worker_name = "MOCK_WORKER"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        worker = workers[0]

        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker potentially re-registered")
        worker_id = workers[0].db_id

        self.assertEqual(len(task_runner.running_assignments), 0)

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent was not created properly")

        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent may have been duplicated")
        agent = agents[0]
        self.assertIsNotNone(agent)
        self.assertEqual(len(sup.agents), 1, "Agent not registered with supervisor")

        self.assertEqual(
            len(task_runner.running_units), 1, "Ready task was not launched"
        )

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id = workers[0].db_id

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)

        self.assertEqual(len(task_runner.running_units), 2, "Tasks were not launched")
        agents = [a.agent for a in sup.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})

        # Give up to 1 seconds for the actual operations to occur
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(agent_1_data["acts"]) > 0:
                break
            time.sleep(0.1)

        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not process messages in time"
        )

        # Give up to 1 seconds for the task to complete afterwards
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(task_runner.running_units) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not complete task in time"
        )

        # Give up to 1 seconds for all messages to propogate
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if self.architect.server.actions_observed == 2:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Not all actions observed in time"
        )

        sup.shutdown()
        self.assertTrue(channel_info.channel.is_closed)

    def test_register_job(self):
        """Test registering and running a job run asynchronously"""
        # Handle baseline setup
        sup = Supervisor(self.db)
        self.sup = sup
        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        args = MockBlueprint.ArgsClass()
        args.timeout_time = 5
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        task_runner = TaskRunnerClass(self.task_run, config, EMPTY_STATE)
        sup.register_job(self.architect, task_runner, self.provider)
        self.assertEqual(len(sup.channels), 1)
        channel_info = list(sup.channels.values())[0]
        self.assertIsNotNone(channel_info)
        self.assertTrue(channel_info.channel.is_alive())
        channel_id = channel_info.channel_id
        task_runner = channel_info.job.task_runner
        self.assertIsNotNone(channel_id)
        self.assertEqual(
            len(self.architect.server.subs),
            1,
            "MockServer doesn't see registered channel",
        )
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )
        sup.launch_sending_thread()
        self.assertIsNotNone(sup.sending_thread)

        # Register a worker
        mock_worker_name = "MOCK_WORKER"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        worker = workers[0]

        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker potentially re-registered")
        worker_id = workers[0].db_id

        self.assertEqual(len(task_runner.running_assignments), 0)

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent was not created properly")

        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent may have been duplicated")
        agent = agents[0]
        self.assertIsNotNone(agent)
        self.assertEqual(len(sup.agents), 1, "Agent not registered with supervisor")

        self.assertEqual(
            len(task_runner.running_assignments), 0, "Task was not yet ready"
        )

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_id = workers[0].db_id

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)

        self.assertEqual(
            len(task_runner.running_assignments), 1, "Task was not launched"
        )
        agents = [a.agent for a in sup.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})

        # Give up to 1 seconds for the actual operation to occur
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(agent_1_data["acts"]) > 0:
                break
            time.sleep(0.1)

        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not process messages in time"
        )

        # Give up to 1 seconds for the task to complete afterwards
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(task_runner.running_assignments) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not complete task in time"
        )

        # Give up to 1 seconds for all messages to propogate
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if self.architect.server.actions_observed == 2:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Not all actions observed in time"
        )

        sup.shutdown()
        self.assertTrue(channel_info.channel.is_closed())

    def test_register_concurrent_job_with_onboarding(self):
        """Test registering and running a job with onboarding"""
        # Handle baseline setup
        sup = Supervisor(self.db)
        self.sup = sup
        TEST_QUALIFICATION_NAME = "test_onboarding_qualification"

        task_run_args = self.task_run.args
        task_run_args.blueprint.use_onboarding = True
        task_run_args.blueprint.onboarding_qualification = TEST_QUALIFICATION_NAME
        task_run_args.blueprint.timeout_time = 5
        task_run_args.blueprint.is_concurrent = True
        self.task_run.get_task_config()

        # Supervisor expects that blueprint setup has already occurred
        blueprint = self.task_run.get_blueprint()

        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        task_runner = TaskRunnerClass(self.task_run, task_run_args, EMPTY_STATE)

        sup.register_job(self.architect, task_runner, self.provider)
        self.assertEqual(len(sup.channels), 1)
        channel_info = list(sup.channels.values())[0]
        self.assertIsNotNone(channel_info)
        self.assertTrue(channel_info.channel.is_alive())
        channel_id = channel_info.channel_id
        task_runner = channel_info.job.task_runner
        self.assertIsNotNone(channel_id)
        self.assertEqual(
            len(self.architect.server.subs),
            1,
            "MockServer doesn't see registered channel",
        )
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )
        sup.launch_sending_thread()
        self.assertIsNotNone(sup.sending_thread)

        self.assertEqual(len(task_runner.running_units), 0)

        # Fail to register an agent who fails onboarding
        mock_worker_name = "BAD_WORKER"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        worker_0 = workers[0]

        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker potentially re-registered")
        worker_id = workers[0].db_id

        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents), 0, "Agent should not be created yet - need onboarding"
        )
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(
            len(onboard_agents), 1, "Onboarding agent should have been created"
        )
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": False}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_id, onboard_agents[0].get_agent_id(), onboard_data
        )
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")
        self.assertEqual(len(sup.agents), 0, "Failed agent registered with supervisor")

        self.assertEqual(
            len(task_runner.running_units),
            0,
            "Task should not launch with failed worker",
        )

        # Register a worker
        mock_worker_name = "MOCK_WORKER"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        worker_1 = workers[0]

        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker potentially re-registered")
        worker_id = workers[0].db_id

        self.assertEqual(len(task_runner.running_assignments), 0)

        # Fail to register a blocked agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        qualification_id = blueprint.onboarding_qualification_id
        self.db.grant_qualification(qualification_id, worker_1.db_id, 0)
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents), 0, "Agent should not be created yet, failed onboarding"
        )
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertNotIn(
            "onboard_data",
            last_packet["data"],
            "Onboarding triggered for disqualified worker",
        )
        self.assertIsNone(
            last_packet["data"]["agent_id"], "worker assigned real agent id"
        )
        self.architect.server.last_packet = None
        self.db.revoke_qualification(qualification_id, worker_id)

        # Register an onboarding agent successfully
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents), 0, "Agent should not be created yet - need onboarding"
        )
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(
            len(onboard_agents), 2, "Onboarding agent should have been created"
        )
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": True}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_id, onboard_agents[1].get_agent_id(), onboard_data
        )
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent not created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent may have been duplicated")
        agent = agents[0]
        self.assertIsNotNone(agent)
        self.assertEqual(len(sup.agents), 1, "Agent not registered with supervisor")

        self.assertEqual(
            len(task_runner.running_assignments),
            0,
            "Task was not yet ready, should not launch",
        )

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_2 = workers[0]
        worker_id = worker_2.db_id

        # Register an agent that is already qualified
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        self.db.grant_qualification(qualification_id, worker_2.db_id, 1)
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertNotIn(
            "onboard_data",
            last_packet["data"],
            "Onboarding triggered for qualified agent",
        )
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Second agent not created without onboarding")

        self.assertEqual(
            len(task_runner.running_assignments), 1, "Task was not launched"
        )

        self.assertFalse(worker_0.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_0.is_disqualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_1.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertFalse(worker_1.is_disqualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_2.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertFalse(worker_2.is_disqualified(TEST_QUALIFICATION_NAME))
        agents = [a.agent for a in sup.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})

        # Give up to 1 seconds for the actual operation to occur
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(agent_1_data["acts"]) > 0:
                break
            time.sleep(0.1)

        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not process messages in time"
        )

        # Give up to 1 seconds for the task to complete afterwards
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(task_runner.running_assignments) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not complete task in time"
        )

        # Give up to 1 seconds for all messages to propogate
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if self.architect.server.actions_observed == 2:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Not all actions observed in time"
        )

        sup.shutdown()
        self.assertTrue(channel_info.channel.is_closed())

    def test_register_job_with_onboarding(self):
        """Test registering and running a job with onboarding"""
        # Handle baseline setup
        sup = Supervisor(self.db)
        self.sup = sup
        TEST_QUALIFICATION_NAME = "test_onboarding_qualification"

        # Register onboarding arguments for blueprint
        task_run_args = self.task_run.args
        task_run_args.blueprint.use_onboarding = True
        task_run_args.blueprint.onboarding_qualification = TEST_QUALIFICATION_NAME
        task_run_args.blueprint.timeout_time = 5
        task_run_args.blueprint.is_concurrent = False
        self.task_run.get_task_config()

        # Supervisor expects that blueprint setup has already occurred
        blueprint = self.task_run.get_blueprint()

        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        task_runner = TaskRunnerClass(self.task_run, task_run_args, EMPTY_STATE)
        sup.register_job(self.architect, task_runner, self.provider)
        self.assertEqual(len(sup.channels), 1)
        channel_info = list(sup.channels.values())[0]
        self.assertIsNotNone(channel_info)
        self.assertTrue(channel_info.channel.is_alive())
        channel_id = channel_info.channel_id
        task_runner = channel_info.job.task_runner
        self.assertIsNotNone(channel_id)
        self.assertEqual(
            len(self.architect.server.subs),
            1,
            "MockServer doesn't see registered channel",
        )
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )
        sup.launch_sending_thread()
        self.assertIsNotNone(sup.sending_thread)

        # Register a worker
        mock_worker_name = "MOCK_WORKER"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        worker_1 = workers[0]

        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        self.assertEqual(len(workers), 1, "Worker potentially re-registered")
        worker_id = workers[0].db_id

        self.assertEqual(len(task_runner.running_units), 0)

        # Fail to register a blocked agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        qualification_id = blueprint.onboarding_qualification_id
        self.db.grant_qualification(qualification_id, worker_1.db_id, 0)
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents), 0, "Agent should not be created yet, failed onboarding"
        )
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertNotIn(
            "onboard_data",
            last_packet["data"],
            "Onboarding triggered for disqualified worker",
        )
        self.assertIsNone(
            last_packet["data"]["agent_id"], "worker assigned real agent id"
        )
        self.architect.server.last_packet = None
        self.db.revoke_qualification(qualification_id, worker_id)

        # Register an agent successfully
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents), 0, "Agent should not be created yet - need onboarding"
        )
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(
            len(onboard_agents), 1, "Onboarding agent should have been created"
        )
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": False}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_id, onboard_agents[0].get_agent_id(), onboard_data
        )
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")
        self.assertEqual(len(sup.agents), 0, "Failed agent registered with supervisor")

        self.assertEqual(
            len(task_runner.running_units),
            0,
            "Task should not launch with failed worker",
        )

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_2 = workers[0]
        worker_id = worker_2.db_id

        # Register an agent that is already qualified
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        self.db.grant_qualification(qualification_id, worker_2.db_id, 1)
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertNotIn(
            "onboard_data",
            last_packet["data"],
            "Onboarding triggered for qualified agent",
        )
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Second agent not created without onboarding")

        self.assertEqual(len(task_runner.running_units), 1, "Tasks were not launched")

        self.assertFalse(worker_1.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_1.is_disqualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_2.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertFalse(worker_2.is_disqualified(TEST_QUALIFICATION_NAME))

        # Register another worker
        mock_worker_name = "MOCK_WORKER_3"
        self.architect.server.register_mock_worker(mock_worker_name)
        workers = self.db.find_workers(worker_name=mock_worker_name)
        worker_3 = workers[0]
        worker_id = worker_3.db_id
        mock_agent_details = "FAKE_ASSIGNMENT_3"
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(
            len(agents), 1, "Agent should not be created yet - need onboarding"
        )
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(
            len(onboard_agents), 2, "Onboarding agent should have been created"
        )
        time.sleep(0.1)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": True}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_id, onboard_agents[1].get_agent_id(), onboard_data
        )
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Agent not created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(worker_id, mock_agent_details)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Duplicate agent created after onboarding")
        agent = agents[1]
        self.assertIsNotNone(agent)
        self.assertEqual(
            len(sup.agents), 2, "Agent not registered supervisor after onboarding"
        )

        self.assertEqual(
            len(task_runner.running_units), 2, "Task not launched after onboarding"
        )

        agents = [a.agent for a in sup.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})

        # Give up to 1 seconds for the actual operation to occur
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(agent_1_data["acts"]) > 0:
                break
            time.sleep(0.1)

        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not process messages in time"
        )

        # Give up to 1 seconds for the task to complete afterwards
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if len(task_runner.running_units) == 0:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Did not complete task in time"
        )

        # Give up to 1 seconds for all messages to propogate
        start_time = time.time()
        TIMEOUT_TIME = 1
        while time.time() - start_time < TIMEOUT_TIME:
            if self.architect.server.actions_observed == 2:
                break
            time.sleep(0.1)
        self.assertLess(
            time.time() - start_time, TIMEOUT_TIME, "Not all actions observed in time"
        )

        sup.shutdown()
        self.assertTrue(channel_info.channel.is_closed())

    # TODO(#97) handle testing for disconnecting in and out of tasks


class TestSupervisorLocal(BaseTestSupervisor, unittest.TestCase):
    DB_CLASS = LocalMephistoDB


class TestSupervisorSingleton(BaseTestSupervisor, unittest.TestCase):
    DB_CLASS = MephistoSingletonDB


if __name__ == "__main__":
    unittest.main()
