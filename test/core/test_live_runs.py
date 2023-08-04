#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
import shutil
import os
import tempfile
import time
import asyncio

from typing import List, Callable

from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.blueprints.mock.mock_task_runner import MockTaskRunner
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.databases.local_singleton_database import MephistoSingletonDB
from mephisto.operations.task_launcher import TaskLauncher, SCREENING_UNIT_INDEX
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.utils.testing import get_test_task_run
from mephisto.data_model.assignment import InitializationData
from mephisto.data_model.worker import Worker
from mephisto.data_model.task_run import TaskRun
from mephisto.operations.datatypes import LiveTaskRun, LoopWrapper
from mephisto.operations.client_io_handler import ClientIOHandler
from mephisto.operations.worker_pool import WorkerPool

from mephisto.abstractions.architects.mock_architect import (
    MockArchitect,
    MockArchitectArgs,
)
from mephisto.operations.hydra_config import MephistoConfig
from mephisto.abstractions.providers.mock.mock_provider import (
    MockProvider,
    MockProviderArgs,
)
from mephisto.abstractions.blueprints.mock.mock_blueprint import (
    MockBlueprint,
    MockBlueprintArgs,
    MockSharedState,
)
from omegaconf import OmegaConf

from typing import Type, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB

EMPTY_STATE = MockSharedState()


class BaseTestLiveRuns:
    """
    Unit testing for the Mephisto Live Runs,
    uses WebsocketChannel and MockArchitect
    """

    DB_CLASS: ClassVar[Type["MephistoDB"]]

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        assert self.DB_CLASS is not None, "Did not specify db to use"
        self.db = self.DB_CLASS(database_path)
        self.task_id = self.db.new_task("test_mock", MockBlueprint.BLUEPRINT_TYPE)
        self.task_run_id = get_test_task_run(self.db)
        self.task_run = TaskRun.get(self.db, self.task_run_id)
        self.live_run = None

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
        self.launcher = TaskLauncher(self.db, self.task_run, self.get_mock_assignment_data_array())
        self.launcher.create_assignments()
        self.launcher.launch_units(self.url)
        self.client_io = ClientIOHandler(self.db)
        self.worker_pool = WorkerPool(self.db)

    def tearDown(self):
        self.launcher.expire_units()
        self.architect.cleanup()
        self.architect.shutdown()
        if self.live_run is not None:
            self.live_run.shutdown()
        else:
            self.worker_pool.shutdown()
            self.client_io.shutdown()
        self.db.shutdown()
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def get_mock_run(self, blueprint, task_runner) -> LiveTaskRun:
        live_run = LiveTaskRun(
            self.task_run,
            self.architect,
            blueprint,
            self.provider,
            [],
            task_runner,
            self.launcher,
            self.client_io,
            self.worker_pool,
            LoopWrapper(asyncio.new_event_loop()),
        )
        self.client_io.register_run(live_run)
        self.worker_pool.register_run(live_run)
        return live_run

    def assert_server_subbed_in_time(self, server, timeout: int = 5) -> None:
        start_time = time.time()
        while (len(server.subs) == 0) and time.time() - start_time < timeout:
            time.sleep(0.3)
        self.assertEqual(
            len(self.architect.server.subs),
            1,
            "MockServer doesn't see registered channel",
        )

    def get_mock_assignment_data_array(self) -> List[InitializationData]:
        mock_data = MockTaskRunner.get_mock_assignment_data()
        return [mock_data, mock_data]

    def make_registered_worker(self, worker_name) -> Worker:
        worker_id = self.db.new_worker(worker_name + "_sandbox", "mock")
        return Worker.get(self.db, worker_id)

    def _run_loop_until(
        self,
        live_run: LiveTaskRun,
        condition_met: Callable[[], bool],
        timeout,
        failure_message=None,
    ) -> bool:
        """
        Function to run the event loop until a specific condition is met, or
        a timeout elapses
        """
        loop = live_run.loop_wrap.loop
        asyncio.set_event_loop(loop)

        async def wait_for_condition_or_timeout():
            condition_was_met = False
            start_time = time.time()
            while time.time() - start_time < timeout:
                await asyncio.sleep(0.01)
                if condition_met():
                    condition_was_met = True
                    break
                await asyncio.sleep(0.2)
            return condition_was_met

        return loop.run_until_complete(wait_for_condition_or_timeout())

    def assert_sandbox_worker_created(self, live_run, worker_name, timeout=2) -> None:
        self.assertTrue(  # type: ignore
            self._run_loop_until(
                live_run,
                lambda: len(self.db.find_workers(worker_name=worker_name + "_sandbox")) > 0,
                timeout,
            ),
            f"Worker {worker_name} not created in time!",
        )

    def assert_agent_created(self, live_run, agent_num, timeout=2) -> None:
        self.assertTrue(  # type: ignore
            self._run_loop_until(
                live_run,
                lambda: len(self.db.find_agents()) == agent_num,
                timeout,
            ),
            f"Agent {agent_num} not created in time!",
        )
        agents = self.db.find_agents()
        agent = agents[agent_num - 1]
        self.assertIsNotNone(agent)  # type: ignore

    def _await_current_tasks(self, live_run, timeout=5) -> None:
        self._run_loop_until(
            live_run,
            lambda: len(asyncio.all_tasks(live_run.loop_wrap.loop)) < 3,
            timeout,
        )

    def await_channel_requests(self, live_run, timeout=2) -> None:
        self._await_current_tasks(live_run, timeout)
        self.assertTrue(  # type: ignore
            self._run_loop_until(
                live_run,
                lambda: len(live_run.client_io.request_id_to_channel_id) == 0,
                timeout,
            ),
            f"Channeled requests not processed in time!",
        )

    def test_channel_operations(self):
        """
        Initialize a channel, and ensure the basic
        startup and shutdown functions are working
        """
        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        args = MockBlueprint.ArgsClass()
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        task_runner = TaskRunnerClass(self.task_run, config, EMPTY_STATE)

        channels = self.architect.get_channels(
            self.client_io._on_channel_open,
            self.client_io._on_catastrophic_disconnect,
            self.client_io._on_message,
        )
        channel = channels[0]
        self.client_io._register_channel(channel)
        self.assertTrue(channel.is_alive())
        channel.close()
        self.assertTrue(channel.is_closed())

    def test_register_concurrent_run(self):
        """Test registering and running a run that requires multiple workers"""
        # Handle baseline setup
        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        args = MockBlueprint.ArgsClass()
        args.timeout_time = 5
        args.is_concurrent = False
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        task_runner = TaskRunnerClass(self.task_run, config, EMPTY_STATE)
        blueprint = self.task_run.get_blueprint()
        live_run = self.get_mock_run(blueprint, task_runner)
        self.live_run = live_run
        live_run.client_io.launch_channels()
        self.assertEqual(len(live_run.client_io.channels), 1)
        channel = list(live_run.client_io.channels.values())[0]
        self.assertIsNotNone(channel)
        self.assertTrue(channel.is_alive())
        task_runner = live_run.task_runner
        self.assert_server_subbed_in_time(self.architect.server)
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )

        # Register a worker
        mock_worker_name = "MOCK_WORKER"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        workers = self.db.find_workers(worker_name=mock_worker_name + "_sandbox")
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent was not created properly")

        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        workers = self.db.find_workers(worker_name=mock_worker_name + "_sandbox")
        self.assertEqual(len(workers), 1, "Worker potentially re-registered")
        self.assertEqual(len(agents), 1, "Agent may have been duplicated")
        agent = agents[0]
        self.assertIsNotNone(agent)
        self.assertEqual(
            len(live_run.worker_pool.agents), 1, "Agent not registered with worker pool"
        )

        self.assertEqual(len(task_runner.running_units), 1, "Ready task was not launched")

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)

        self.assertEqual(len(task_runner.running_units), 2, "Tasks were not launched")
        agents = [a for a in live_run.worker_pool.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})
        self.await_channel_requests(live_run)

        # Give up to 1 seconds for the actual operations to occur
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(agent_1_data["acts"]) > 0,
                1,
            ),
            "Did not process messages in time",
        )
        self.architect.server.submit_mock_unit(agent_id_1, {"completed": True})
        self.architect.server.submit_mock_unit(agent_id_2, {"completed": True})
        self.await_channel_requests(live_run)

        # Give up to 1 seconds for the task to complete afterwards
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(task_runner.running_units) == 0,
                1,
            ),
            "Did not complete task in time",
        )

        # Give up to 1 seconds for all messages to propogate
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: self.architect.server.actions_observed == 2,
                1,
            ),
            "Not all actions observed in time",
        )

        live_run.shutdown()
        self.assertTrue(channel.is_closed)

    def test_register_run(self):
        """Test registering and running a task run asynchronously"""
        # Handle baseline setup
        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        args = MockBlueprint.ArgsClass()
        args.timeout_time = 5
        config = OmegaConf.structured(MephistoConfig(blueprint=args))
        task_runner = TaskRunnerClass(self.task_run, config, EMPTY_STATE)
        blueprint = self.task_run.get_blueprint(args=config)
        live_run = self.get_mock_run(blueprint, task_runner)
        self.live_run = live_run
        live_run.client_io.launch_channels()
        self.assertEqual(len(live_run.client_io.channels), 1)
        channel = list(live_run.client_io.channels.values())[0]
        self.assertIsNotNone(channel)
        self.assertTrue(channel.is_alive())
        task_runner = live_run.task_runner
        self.assert_server_subbed_in_time(self.architect.server)
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )

        # Register a worker
        mock_worker_name = "MOCK_WORKER"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        workers = self.db.find_workers(worker_name=mock_worker_name + "_sandbox")
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent was not created properly")

        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent may have been duplicated")
        agent = agents[0]
        self.assertIsNotNone(agent)
        self.assertEqual(len(self.worker_pool.agents), 1, "Agent not registered with worker pool")

        self.assertEqual(len(task_runner.running_assignments), 0, "Task was not yet ready")

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"

        # Register an agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)

        self.assertEqual(len(task_runner.running_assignments), 1, "Task was not launched")
        agents = [a for a in self.worker_pool.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})
        self.await_channel_requests(live_run)

        # Give up to 1 seconds for the actual operation to occur
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(agent_1_data["acts"]) > 0,
                1,
            ),
            "Did not process messages in time",
        )

        self.architect.server.submit_mock_unit(agent_id_1, {"completed": True})
        self.architect.server.submit_mock_unit(agent_id_2, {"completed": True})

        # Give up to 1 seconds for the task to complete afterwards
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(task_runner.running_assignments) == 0,
                1,
            ),
            "Did not complete task in time",
        )

        # Give up to 1 seconds for all messages to propogate
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: self.architect.server.actions_observed == 2,
                1,
            ),
            "Not all actions observed in time",
        )

        live_run.shutdown()
        self.assertTrue(channel.is_closed())

    def test_register_concurrent_run_with_onboarding(self):
        """Test registering and running a run with onboarding"""
        # Handle baseline setup
        TEST_QUALIFICATION_NAME = "test_onboarding_qualification"

        task_run_args = self.task_run.args
        task_run_args.blueprint.use_onboarding = True
        task_run_args.blueprint.onboarding_qualification = TEST_QUALIFICATION_NAME
        task_run_args.blueprint.timeout_time = 5
        task_run_args.blueprint.is_concurrent = True

        # LiveTaskRun expects that blueprint setup has already occurred
        blueprint = self.task_run.get_blueprint()

        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        task_runner = TaskRunnerClass(self.task_run, task_run_args, EMPTY_STATE)

        live_run = self.get_mock_run(blueprint, task_runner)
        self.live_run = live_run
        live_run.client_io.launch_channels()
        self.assertEqual(len(live_run.client_io.channels), 1)
        channel = list(live_run.client_io.channels.values())[0]
        self.assertIsNotNone(channel)
        self.assertTrue(channel.is_alive())
        task_runner = live_run.task_runner
        self.assert_server_subbed_in_time(self.architect.server)
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )

        self.assertEqual(len(task_runner.running_units), 0)

        # Fail to register an agent who fails onboarding
        mock_worker_name = "BAD_WORKER"

        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        workers = self.db.find_workers(worker_name=mock_worker_name + "_sandbox")
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        worker_0 = workers[0]
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Agent should not be created yet - need onboarding")
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(len(onboard_agents), 1, "Onboarding agent should have been created")

        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        if not last_packet["data"].get("status") == "onboarding":
            self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": False}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_0.db_id, onboard_agents[0].get_agent_id(), onboard_data
        )
        self.await_channel_requests(live_run, 4)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(worker_0.db_id, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")
        self.assertEqual(
            len(self.worker_pool.agents), 0, "Failed agent registered with worker pool"
        )

        self.assertEqual(
            len(task_runner.running_units),
            0,
            "Task should not launch with failed worker",
        )

        # Register a worker
        mock_worker_name = "MOCK_WORKER"
        worker_1 = self.make_registered_worker(mock_worker_name)

        # Fail to register a blocked agent
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        qualification_id = blueprint.onboarding_qualification_id
        self.db.grant_qualification(qualification_id, worker_1.db_id, 0)
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Agent should not be created yet, failed onboarding")

        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertNotIn(
            "onboard_data",
            last_packet["data"],
            "Onboarding triggered for disqualified worker",
        )
        self.assertIsNone(last_packet["data"]["agent_id"], "worker assigned real agent id")
        self.architect.server.last_packet = None
        self.db.revoke_qualification(qualification_id, worker_1.db_id)

        # Register an onboarding agent successfully
        mock_agent_details = "FAKE_ASSIGNMENT_3"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Agent should not be created yet - need onboarding")
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(len(onboard_agents), 2, "Onboarding agent should have been created")

        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        if not last_packet["data"].get("status") == "onboarding":
            self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": True}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_1.db_id, onboard_agents[1].get_agent_id(), onboard_data
        )
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent not created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent may have been duplicated")
        agent = agents[0]
        self.assertIsNotNone(agent)
        self.assertEqual(len(self.worker_pool.agents), 1, "Agent not registered with worker pool")

        self.assertEqual(
            len(task_runner.running_assignments),
            0,
            "Task was not yet ready, should not launch",
        )

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        worker_2 = self.make_registered_worker(mock_worker_name)

        # Register an agent that is already qualified
        mock_agent_details = "FAKE_ASSIGNMENT_4"
        self.db.grant_qualification(qualification_id, worker_2.db_id, 1)
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)

        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertNotIn(
            "onboard_data",
            last_packet["data"],
            "Onboarding triggered for qualified agent",
        )
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Second agent not created without onboarding")

        self.assertEqual(len(task_runner.running_assignments), 1, "Task was not launched")

        self.assertFalse(worker_0.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_0.is_disqualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_1.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertFalse(worker_1.is_disqualified(TEST_QUALIFICATION_NAME))
        self.assertTrue(worker_2.is_qualified(TEST_QUALIFICATION_NAME))
        self.assertFalse(worker_2.is_disqualified(TEST_QUALIFICATION_NAME))
        agents = [a for a in self.worker_pool.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})
        self.await_channel_requests(live_run)

        # Give up to 1 seconds for the actual operation to occur
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(agent_1_data["acts"]) > 0,
                1,
            ),
            "Did not process messages in time",
        )

        self.architect.server.submit_mock_unit(agent_id_1, {"completed": True})
        self.architect.server.submit_mock_unit(agent_id_2, {"completed": True})

        # Give up to 1 seconds for the task to complete afterwards
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(task_runner.running_assignments) == 0,
                1,
            ),
            "Did not complete task in time",
        )

        # Give up to 1 seconds for all messages to propogate
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: self.architect.server.actions_observed == 2,
                1,
            ),
            "Not all actions observed in time",
        )

        live_run.shutdown()
        self.assertTrue(channel.is_closed())

    def test_register_run_with_onboarding(self):
        """Test registering and running a run with onboarding"""
        # Handle baseline setup
        TEST_QUALIFICATION_NAME = "test_onboarding_qualification"

        # Register onboarding arguments for blueprint
        task_run_args = self.task_run.args
        task_run_args.blueprint.use_onboarding = True
        task_run_args.blueprint.onboarding_qualification = TEST_QUALIFICATION_NAME
        task_run_args.blueprint.timeout_time = 5
        task_run_args.blueprint.is_concurrent = False

        # LiveTaskRun expects that blueprint setup has already occurred
        blueprint = self.task_run.get_blueprint()

        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        task_runner = TaskRunnerClass(self.task_run, task_run_args, EMPTY_STATE)
        live_run = self.get_mock_run(blueprint, task_runner)
        self.live_run = live_run
        live_run.client_io.launch_channels()
        self.assertEqual(len(live_run.client_io.channels), 1)
        channel = list(live_run.client_io.channels.values())[0]
        self.assertIsNotNone(channel)
        self.assertTrue(channel.is_alive())
        task_runner = live_run.task_runner
        self.assert_server_subbed_in_time(self.architect.server)
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )

        # Register a worker
        mock_worker_name = "MOCK_WORKER"
        worker_1 = self.make_registered_worker(mock_worker_name)

        self.assertEqual(len(task_runner.running_units), 0)

        # Fail to register a blocked agent
        mock_agent_details = "FAKE_ASSIGNMENT"
        qualification_id = blueprint.onboarding_qualification_id
        self.db.grant_qualification(qualification_id, worker_1.db_id, 0)
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Agent should not be created yet, failed onboarding")

        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        self.assertNotIn(
            "onboard_data",
            last_packet["data"],
            "Onboarding triggered for disqualified worker",
        )
        self.assertIsNone(last_packet["data"]["agent_id"], "worker assigned real agent id")
        self.architect.server.last_packet = None
        self.db.revoke_qualification(qualification_id, worker_1.db_id)

        # Register an agent successfully
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Agent should not be created yet - need onboarding")
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(len(onboard_agents), 1, "Onboarding agent should have been created")

        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        if not last_packet["data"].get("status") == "onboarding":
            self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": False}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_1.db_id, onboard_agents[0].get_agent_id(), onboard_data
        )
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 0, "Failed agent created after onboarding")
        self.assertEqual(
            len(self.worker_pool.agents), 0, "Failed agent registered with worker pool"
        )

        self.assertEqual(
            len(task_runner.running_units),
            0,
            "Task should not launch with failed worker",
        )

        # Register another worker
        mock_worker_name = "MOCK_WORKER_2"
        worker_2 = self.make_registered_worker(mock_worker_name)

        # Register an agent that is already qualified
        mock_agent_details = "FAKE_ASSIGNMENT_2"
        self.db.grant_qualification(qualification_id, worker_2.db_id, 1)
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)

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
        mock_agent_details = "FAKE_ASSIGNMENT_3"
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        workers = self.db.find_workers(worker_name=mock_worker_name + "_sandbox")
        worker_3 = workers[0]
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "Agent should not be created yet - need onboarding")
        onboard_agents = self.db.find_onboarding_agents()
        self.assertEqual(len(onboard_agents), 2, "Onboarding agent should have been created")
        self._await_current_tasks(live_run, 2)
        last_packet = self.architect.server.last_packet
        self.assertIsNotNone(last_packet)
        if not last_packet["data"].get("status") == "onboarding":
            self.assertIn("onboard_data", last_packet["data"], "Onboarding not triggered")
        self.architect.server.last_packet = None

        # Submit onboarding from the agent
        onboard_data = {"should_pass": True}
        self.architect.server.register_mock_agent_after_onboarding(
            worker_2.db_id, onboard_agents[1].get_agent_id(), onboard_data
        )
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Agent not created after onboarding")

        # Re-register as if refreshing
        self.architect.server.register_mock_agent(mock_worker_name, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Duplicate agent created after onboarding")
        agent = agents[1]
        self.assertIsNotNone(agent)
        self.assertEqual(
            len(self.worker_pool.agents),
            2,
            "Agent not registered to worker pool after onboarding",
        )

        self.assertEqual(len(task_runner.running_units), 2, "Task not launched after onboarding")

        agents = [a for a in self.worker_pool.agents.values()]

        # Make both agents act
        agent_id_1, agent_id_2 = agents[0].db_id, agents[1].db_id
        agent_1_data = agents[0].datastore.agent_data[agent_id_1]
        agent_2_data = agents[1].datastore.agent_data[agent_id_2]
        self.architect.server.send_agent_act(agent_id_1, {"text": "message1"})
        self.architect.server.send_agent_act(agent_id_2, {"text": "message2"})
        self.await_channel_requests(live_run)

        # Give up to 1 seconds for the actual operation to occur
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(agent_1_data["acts"]) > 0,
                1,
            ),
            "Did not process messages in time",
        )

        self.architect.server.submit_mock_unit(agent_id_1, {"completed": True})
        self.architect.server.submit_mock_unit(agent_id_2, {"completed": True})

        # Give up to 1 seconds for the task to complete afterwards
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: len(task_runner.running_units) == 0,
                1,
            ),
            "Did not complete task in time",
        )

        # Give up to 1 seconds for all messages to propogate
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: self.architect.server.actions_observed == 2,
                1,
            ),
            "Not all actions observed in time",
        )

        live_run.shutdown()
        self.assertTrue(channel.is_closed())

    def test_register_run_with_screening(self):
        """Test registering and running a run with screening"""
        if self.DB_CLASS != MephistoSingletonDB:
            # TODO(#97) This test only works with singleton for now due to disconnect simulation
            return

        # Handle baseline setup
        PASSED_QUALIFICATION_NAME = "test_screening_qualification"
        FAILED_QUALIFICATION_NAME = "failed_screening_qualification"

        # Register onboarding arguments for blueprint
        task_run_args = self.task_run.args
        task_run_args.blueprint.use_screening_task = True
        task_run_args.blueprint.passed_qualification_name = PASSED_QUALIFICATION_NAME
        task_run_args.blueprint.block_qualification = FAILED_QUALIFICATION_NAME
        task_run_args.blueprint.max_screening_units = 2
        task_run_args.blueprint.timeout_time = 5
        task_run_args.blueprint.is_concurrent = False

        def screen_unit(unit):
            if unit.get_assigned_agent() is None:
                return None  # No real data to evaluate

            agent = unit.get_assigned_agent()
            output = agent.state.get_data()
            if output is None:
                return None  # no data to evaluate

            return output["success"]

        shared_state = MockSharedState()
        shared_state.on_unit_submitted = ScreenTaskRequired.create_validation_function(
            task_run_args,
            screen_unit,
        )

        # LiveTaskRun expects that blueprint setup has already occurred
        blueprint = self.task_run.get_blueprint(task_run_args, shared_state)

        TaskRunnerClass = MockBlueprint.TaskRunnerClass
        task_runner = TaskRunnerClass(self.task_run, task_run_args, shared_state)
        live_run = self.get_mock_run(blueprint, task_runner)
        self.live_run = live_run
        live_run.client_io.launch_channels()
        self.assertEqual(len(live_run.client_io.channels), 1)
        channel = list(live_run.client_io.channels.values())[0]
        self.assertIsNotNone(channel)
        self.assertTrue(channel.is_alive())
        task_runner = live_run.task_runner
        self.assert_server_subbed_in_time(self.architect.server)
        self.assertIsNotNone(
            self.architect.server.last_alive_packet,
            "No alive packet received by server",
        )

        # Register workers
        mock_worker_name_1 = "MOCK_WORKER"
        mock_worker_name_2 = "MOCK_WORKER_2"
        mock_worker_name_3 = "MOCK_WORKER_3"

        # Register a screening agent successfully
        mock_agent_details = "FAKE_ASSIGNMENT"
        self.architect.server.register_mock_agent(mock_worker_name_1, mock_agent_details)
        self.await_channel_requests(live_run)
        workers = self.db.find_workers(worker_name=mock_worker_name_1 + "_sandbox")
        self.assertEqual(len(workers), 1, "Worker not successfully registered")
        worker_1 = workers[0]
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 1, "No agent created for screening")

        self.assertEqual(
            agents[0].get_unit().unit_index,
            SCREENING_UNIT_INDEX,
            "Agent not assigned screening unit",
        )

        # Register a second screening agent successfully
        mock_agent_details = "FAKE_ASSIGNMENT2"
        self.architect.server.register_mock_agent(mock_worker_name_2, mock_agent_details)
        self.await_channel_requests(live_run)
        workers = self.db.find_workers(worker_name=mock_worker_name_2 + "_sandbox")
        worker_2 = workers[0]
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "No agent created for screening")
        last_packet = None

        self.assertEqual(
            agents[1].get_unit().unit_index,
            SCREENING_UNIT_INDEX,
            "Agent not assigned screening unit",
        )

        # Fail to register a third screening agent
        mock_agent_details = "FAKE_ASSIGNMENT3"
        self.architect.server.register_mock_agent(mock_worker_name_3, mock_agent_details)
        self.await_channel_requests(live_run)
        workers = self.db.find_workers(worker_name=mock_worker_name_3 + "_sandbox")
        worker_3 = workers[0]
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 2, "Third agent created, when 2 was max")

        # Disconnect first agent
        agents[0].update_status(AgentState.STATUS_DISCONNECT)

        # Register third screening agent
        mock_agent_details = "FAKE_ASSIGNMENT3"
        self.architect.server.register_mock_agent(mock_worker_name_3, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 3, "Third agent not created")

        self.assertEqual(
            agents[2].get_unit().unit_index,
            SCREENING_UNIT_INDEX,
            "Agent not assigned screening unit",
        )

        # Submit screening from the agent
        screening_data = {"success": False}
        self.architect.server.send_agent_act(agents[1].get_agent_id(), screening_data)
        self.architect.server.submit_mock_unit(agents[1].get_agent_id(), screening_data)
        self.await_channel_requests(live_run)
        # Assert failed screening screening
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: worker_2.is_qualified(FAILED_QUALIFICATION_NAME),
                5,
            ),
            "Did not disqualify in time",
        )

        # Submit screening from the agent
        screening_data = {"success": True}
        self.architect.server.send_agent_act(agents[2].get_agent_id(), screening_data)
        self.architect.server.submit_mock_unit(agents[2].get_agent_id(), screening_data)
        self.await_channel_requests(live_run)
        # Assert successful screening screening
        self.assertTrue(
            self._run_loop_until(
                live_run,
                lambda: worker_3.is_qualified(PASSED_QUALIFICATION_NAME),
                5,
            ),
            "Did not qualify in time",
        )

        # Accept a real task, and complete it, from worker 3
        # Register a task agent successfully
        mock_agent_details = "FAKE_ASSIGNMENT4"
        self.architect.server.register_mock_agent(mock_worker_name_3, mock_agent_details)
        self.await_channel_requests(live_run)
        agents = self.db.find_agents()
        self.assertEqual(len(agents), 4, "No agent created for task")
        last_packet = None

        self.architect.server.send_agent_act(agents[3].get_agent_id(), screening_data)
        self.architect.server.submit_mock_unit(agents[3].get_agent_id(), screening_data)
        self.await_channel_requests(live_run)

        self.assertNotEqual(
            agents[3].get_unit().unit_index,
            SCREENING_UNIT_INDEX,
            "Agent assigned screening unit",
        )

        live_run.shutdown()
        self.assertTrue(channel.is_closed())

    # TODO(#97) handle testing for disconnecting in and out of tasks


class TestLiveRunsLocal(BaseTestLiveRuns, unittest.TestCase):
    DB_CLASS = LocalMephistoDB


class TestLiveRunsSingleton(BaseTestLiveRuns, unittest.TestCase):
    DB_CLASS = MephistoSingletonDB


if __name__ == "__main__":
    unittest.main()
