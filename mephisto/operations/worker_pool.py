#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import threading
import time
from functools import partial
from dataclasses import dataclass
from mephisto.data_model.worker import Worker
from mephisto.data_model.qualification import worker_is_qualified
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.abstractions.blueprint import AgentState
from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
)
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.abstractions.blueprints.mixins.use_gold_unit import UseGoldUnit
from mephisto.operations.task_launcher import (
    SCREENING_UNIT_INDEX,
    GOLD_UNIT_INDEX,
)
from mephisto.operations.datatypes import LiveTaskRun

from typing import Sequence, Dict, Union, Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


@dataclass
class OnboardingInfo:
    crowd_data: Dict[str, Any]
    request_id: str


class WorkerPool:
    """
    The WorkerPool is responsible for tracing the status and state of workers
    and agents that are actively engaged in Mephisto tasks for a given task run. It is
    responsible for delegating to other classes and controllers on particular status
    transitions.
    """

    def __init__(self, db: "MephistoDB"):
        self.db = db
        # Tracked agents
        self.agents: Dict[str, "Agent"] = {}
        self.onboarding_agents: Dict[str, "OnboardingAgent"] = {}
        self.onboarding_infos: Dict[str, OnboardingInfo] = {}
        # Agent status handling
        self.last_status_check = time.time()
        self.agent_status_thread: Optional[threading.Thread] = None

        self.is_shutdown = False

        # Deferred initializiation
        self._live_run: Optional["LiveTaskRun"] = None

    def register_run(self, live_run: "LiveTaskRun") -> None:
        """Register a live run for this worker pool"""
        assert (
            self._live_run is None
        ), "Cannot associate more than one live run to a worker pool at a time"
        self._live_run = live_run

    def get_live_run(self) -> "LiveTaskRun":
        """Get the associated live run for this worker pool, asserting it's set"""
        live_run = self._live_run
        assert live_run is not None, "Live run must be registered to use this"
        return live_run

    async def register_worker(
        self, crowd_data: Dict[str, Any], request_id: str
    ) -> None:
        """Process a worker registration to register a worker"""
        live_run = self.get_live_run()
        loop = live_run.loop_wrap.loop
        crowd_provider = live_run.provider
        is_sandbox = crowd_provider.is_sandbox()
        worker_name = crowd_data["worker_name"]
        if crowd_provider.is_sandbox():
            # TODO there are better ways to get rid of this designation
            worker_name += "_sandbox"
        workers = await loop.run_in_executor(
            None, partial(self.db.find_workers, worker_name=worker_name)
        )
        if len(workers) == 0:
            worker = await loop.run_in_executor(
                None,
                partial(
                    crowd_provider.WorkerClass.new_from_provider_data,
                    self.db,
                    crowd_data,
                ),
            )
        else:
            worker = workers[0]

        is_qualified = await loop.run_in_executor(
            None, partial(worker_is_qualified, worker, live_run.qualifications)
        )
        if not is_qualified:
            await loop.run_in_executor(
                None,
                partial(
                    live_run.client_io.send_provider_details,
                    request_id,
                    {"worker_id": None},
                ),
            )
        else:
            await loop.run_in_executor(
                None,
                partial(
                    live_run.client_io.send_provider_details,
                    request_id,
                    {"worker_id": worker.db_id},
                ),
            )

    async def _assign_unit_to_agent(
        self, crowd_data: Dict[str, Any], request_id: str, units: List["Unit"]
    ):
        live_run = self.get_live_run()
        task_run = live_run.task_run
        loop = live_run.loop_wrap.loop
        crowd_provider = live_run.provider
        worker_id = crowd_data["worker_id"]
        worker = await Worker.async_get(self.db, worker_id)

        logger.debug(f"Worker {worker_id} is being assigned one of {len(units)} units.")

        reserved_unit = None
        while len(units) > 0 and reserved_unit is None:
            unit = units.pop(0)
            reserved_unit = task_run.reserve_unit(unit)
        if reserved_unit is None:
            await loop.run_in_executor(
                None,
                partial(
                    live_run.client_io.send_provider_details,
                    request_id,
                    {"agent_id": None},
                ),
            )
        else:
            agent = await loop.run_in_executor(
                None,
                partial(
                    crowd_provider.AgentClass.new_from_provider_data,
                    self.db,
                    worker,
                    unit,
                    crowd_data,
                ),
            )
            agent.set_live_run(live_run)
            await loop.run_in_executor(
                None,
                partial(
                    live_run.client_io.register_agent_from_request_id,
                    agent.get_agent_id(),
                    request_id,
                    crowd_data["agent_registration_id"],
                ),
            )
            logger.debug(f"Created agent {agent}, {agent.db_id}.")
            await loop.run_in_executor(
                None,
                partial(
                    live_run.client_io.send_provider_details,
                    request_id,
                    {"agent_id": agent.get_agent_id()},
                ),
            )
            self.agents[agent.get_agent_id()] = agent

            # Launch individual tasks
            if unit.unit_index < 0 or not live_run.task_runner.is_concurrent:
                # Run the unit
                live_run.task_runner.execute_unit(
                    unit,
                    agent,
                    lambda: self._mark_agent_done(agent),
                )
            else:
                # See if the concurrent unit is ready to launch
                assignment = await loop.run_in_executor(None, unit.get_assignment)
                agents = await loop.run_in_executor(None, assignment.get_agents)
                if None in agents:
                    agent.update_status(AgentState.STATUS_WAITING)
                    return  # need to wait for all agents to be here to launch

                non_null_agents = [a for a in agents if a is not None]
                # Launch the backend for this assignment
                registered_agents = [
                    self.agents[a.get_agent_id()]
                    for a in non_null_agents
                    if a is not None
                ]

                def mark_agents_done():
                    for agent in registered_agents:
                        self._mark_agent_done(agent)

                live_run.task_runner.execute_assignment(
                    assignment, registered_agents, mark_agents_done
                )

    async def register_agent_from_onboarding(self, onboarding_agent: "OnboardingAgent"):
        """
        Convert the onboarding agent to a full agent
        """
        logger.debug(f"Registering onboarding agent {onboarding_agent}")
        onboarding_id = onboarding_agent.get_agent_id()
        onboarding_agent_info = self.onboarding_agents.get(onboarding_id)

        if onboarding_agent_info is None:
            logger.warning(
                f"Could not find info for onboarding agent {onboarding_id}, "
                "but they submitted onboarding"
            )
            return

        live_run = self.get_live_run()
        loop = live_run.loop_wrap.loop
        blueprint = live_run.blueprint
        worker = onboarding_agent.get_worker()

        assert (
            isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding
        ), "Should only be registering from onboarding if onboarding is required and set"

        # Onboarding validation is run in thread, as we don't know execution time
        worker_passed = await loop.run_in_executor(
            None, partial(blueprint.validate_onboarding, worker, onboarding_agent)
        )

        assert blueprint.onboarding_qualification_name is not None
        worker.grant_qualification(
            blueprint.onboarding_qualification_name, int(worker_passed)
        )
        if not worker_passed:
            worker.grant_qualification(
                blueprint.onboarding_failed_name, int(worker_passed)
            )
            onboarding_agent.update_status(AgentState.STATUS_REJECTED)
            logger.info(f"Onboarding agent {onboarding_id} failed onboarding")
        else:
            onboarding_agent.update_status(AgentState.STATUS_APPROVED)
            logger.info(
                f"Onboarding agent {onboarding_id} registered out from onboarding"
            )

        # get the list of tentatively valid units
        units = await loop.run_in_executor(
            None, partial(live_run.task_run.get_valid_units_for_worker, worker)
        )
        usable_units = await loop.run_in_executor(
            None, partial(live_run.task_runner.filter_units_for_worker, units, worker)
        )

        if not worker_passed:
            # TODO(WISH) it may be worth investigating launching a dummy task for these
            # instances where a worker has failed onboarding, but the onboarding
            # task still allowed submission of the failed data (no front-end validation)
            # units = [self.dummy_launcher.launch_dummy()]
            # self._assign_unit_to_agent(..., units)
            usable_units = []

        onboarding_info = self.onboarding_infos[onboarding_agent.get_agent_id()]
        crowd_data = onboarding_info.crowd_data
        request_id = onboarding_info.request_id

        await self._try_send_agent_messages(onboarding_agent_info)
        await self.push_status_update(onboarding_agent_info)
        if len(usable_units) == 0:
            await loop.run_in_executor(
                None,
                partial(
                    live_run.client_io.send_provider_details,
                    request_id,
                    {"agent_id": None},
                ),
            )
        else:
            await self._assign_unit_to_agent(crowd_data, request_id, usable_units)

    async def register_agent(self, crowd_data: Dict[str, Any], request_id: str):
        """Process an agent registration packet to register an agent, returning the agent_id"""
        # Process a new agent
        logger.debug(f"Registering agent {crowd_data}, {request_id}")
        live_run = self.get_live_run()
        loop = live_run.loop_wrap.loop
        task_run = live_run.task_run
        agent_registration_id = crowd_data["agent_registration_id"]
        worker_id = crowd_data["worker_id"]
        worker = await Worker.async_get(self.db, worker_id)

        # get the list of tentatively valid units
        units = task_run.get_valid_units_for_worker(worker)
        if len(units) == 0:
            await loop.run_in_executor(
                None,
                partial(
                    live_run.client_io.send_provider_details,
                    request_id,
                    {"agent_id": None},
                ),
            )
            logger.debug(
                f"agent_registration_id {agent_registration_id}, had no valid units."
            )
            return

        # If there's onboarding, see if this worker has already been disqualified
        blueprint = live_run.blueprint
        if isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding:
            if worker.is_disqualified(blueprint.onboarding_qualification_name):
                await loop.run_in_executor(
                    None,
                    partial(
                        live_run.client_io.send_provider_details,
                        request_id,
                        {"agent_id": None},
                    ),
                )
                logger.debug(
                    f"Worker {worker_id} is already disqualified by onboarding "
                    f"qual {blueprint.onboarding_qualification_name}."
                )
                return
            elif not worker.is_qualified(blueprint.onboarding_qualification_name):
                # Send a packet with onboarding information
                onboard_data = blueprint.get_onboarding_data(worker.db_id)
                onboard_agent = OnboardingAgent.new(self.db, worker, task_run)
                await loop.run_in_executor(
                    None,
                    partial(
                        live_run.client_io.register_agent_from_request_id,
                        onboard_agent.get_agent_id(),
                        request_id,
                        crowd_data["agent_registration_id"],
                    ),
                )
                onboard_agent.state.set_init_state(onboard_data)
                onboard_agent.set_live_run(live_run)
                onboard_id = onboard_agent.get_agent_id()

                # register onboarding agent
                self.onboarding_agents[onboard_id] = onboard_agent
                self.onboarding_infos[onboard_id] = OnboardingInfo(
                    crowd_data=crowd_data,
                    request_id=request_id,
                )

                await loop.run_in_executor(
                    None,
                    partial(
                        live_run.client_io.send_provider_details,
                        request_id,
                        {
                            "agent_id": onboard_id,
                            "onboard_data": onboard_data,
                        },
                    ),
                )
                logger.info(
                    f"{worker} is starting onboarding thread with "
                    f"onboarding {onboard_agent}."
                )

                async def cleanup_onboarding():
                    del self.onboarding_agents[onboard_id]
                    del self.onboarding_infos[onboard_id]

                # Run the onboarding
                live_run.task_runner.execute_onboarding(
                    onboard_agent, cleanup_onboarding
                )
                return
        if isinstance(blueprint, ScreenTaskRequired) and blueprint.use_screening_task:
            if (
                blueprint.worker_needs_screening(worker)
                and blueprint.should_generate_unit()
            ):
                screening_data = await loop.run_in_executor(
                    None, blueprint.get_screening_unit_data
                )
                if screening_data is not None:
                    launcher = live_run.task_launcher
                    assert (
                        launcher is not None
                    ), "LiveTaskRun must have launcher to use screening tasks"
                    screen_unit = await loop.run_in_executor(
                        None,
                        partial(
                            launcher.launch_screening_unit,
                            screening_data,
                        ),
                    )
                    units = [screen_unit]
                else:
                    await loop.run_in_executor(
                        None,
                        partial(
                            live_run.client_io.send_provider_details,
                            request_id,
                            {"agent_id": None},
                        ),
                    )
                    logger.debug(
                        f"No screening units left for {agent_registration_id}."
                    )
                    return
        if isinstance(blueprint, UseGoldUnit) and blueprint.use_golds:
            if blueprint.should_produce_gold_for_worker(worker):
                gold_data = await loop.run_in_executor(
                    None, partial(blueprint.get_gold_unit_data_for_worker, worker)
                )
                if gold_data is not None:
                    launcher = live_run.task_launcher
                    gold_unit = await loop.run_in_executor(
                        None,
                        partial(
                            launcher.launch_gold_unit,
                            gold_data,
                        ),
                    )
                    units = [gold_unit]
                else:
                    await loop.run_in_executor(
                        None,
                        partial(
                            live_run.client_io.send_provider_details,
                            request_id,
                            {"agent_id": None},
                        ),
                    )
                    logger.debug(f"No gold units left for {agent_registration_id}...")
                    return

        # Not onboarding, so just register directly
        await self._assign_unit_to_agent(crowd_data, request_id, units)

    async def _try_send_agent_messages(self, agent: Union["Agent", "OnboardingAgent"]):
        """Handle sending any possible messages for a specific agent"""
        live_run = self.get_live_run()
        await live_run.loop_wrap.loop.run_in_executor(
            None,
            partial(
                live_run.client_io.send_message_queue,
                agent.pending_observations,
            ),
        )

    async def push_status_update(
        self, agent: Union["Agent", "OnboardingAgent"]
    ) -> None:
        """
        Force a status update for a specific agent, pushing the db status to
        the frontend client
        """
        status = agent.db_status
        if isinstance(agent, OnboardingAgent):
            if status in [AgentState.STATUS_APPROVED, AgentState.STATUS_REJECTED]:
                # We don't expose the updated status directly to the frontend here
                # Can be simplified if we improve how bootstrap-chat handles
                # the transition of onboarding states
                status = AgentState.STATUS_WAITING

        live_run = self.get_live_run()
        await live_run.loop_wrap.loop.run_in_executor(
            None,
            partial(
                live_run.client_io.send_status_update,
                agent.get_agent_id(),
                status,
            ),
        )

    def _mark_agent_done(self, agent: Union["Agent", "OnboardingAgent"]) -> None:
        """
        Handle marking an agent as done, and telling the frontend agent
        that they have successfully completed their task.

        If the agent is in a final non-successful status, or already
        told of partner disconnect, skip
        """
        if agent.db_status in AgentState.complete() + [
            AgentState.STATUS_PARTNER_DISCONNECT
        ]:
            return  # Don't send done messages to agents that are already completed

        live_run = self.get_live_run()
        live_run.client_io.send_done_message(agent.db_id)

    def handle_updated_agent_status(self, status_map: Dict[str, str]):
        """
        Handle updating the local statuses for agents based on
        the previously reported agent statuses.

        Takes as input a mapping from agent_id to server-side status
        """
        live_run = self.get_live_run()
        for agent_id, status in status_map.items():
            if status not in AgentState.valid():
                logger.warning(f"Invalid status for agent {agent_id}: {status}")
                continue
            if agent_id not in self.agents and agent_id not in self.onboarding_agents:
                # no longer tracking agent
                continue
            maybe_agent = self.agents.get(agent_id)
            if maybe_agent is None:
                agent: Union["Agent", "OnboardingAgent"] = self.onboarding_agents[
                    agent_id
                ]
            else:
                agent = maybe_agent
            db_status = agent.get_status()
            if agent.has_updated_status.is_set():
                continue  # Incoming info may be stale if we have new info to send
            if status != db_status:
                if status == AgentState.STATUS_COMPLETED:
                    # Frontend agent completed but hasn't confirmed yet
                    continue
                if status != AgentState.STATUS_DISCONNECT:
                    # Stale or reconnect, send a status update
                    live_run.loop_wrap.execute_coro(
                        self.push_status_update(self.agents[agent_id])
                    )
                    continue  # Only DISCONNECT can be marked remotely, rest are mismatch (except STATUS_COMPLETED)
                agent.update_status(status)
        pass

    def _agent_status_handling_thread(self) -> None:
        """Thread for polling and pushing agent statuses"""
        # TODO rather than polling repeatedly for these, can we use
        # awaits and only trigger this loop when something is ready?
        live_run = self.get_live_run()
        while not self.is_shutdown:
            agents: List[Union["Agent", "OnboardingAgent"]] = list(self.agents.values())
            onboarding_agents: List[Union["Agent", "OnboardingAgent"]] = list(
                self.onboarding_agents.values()
            )
            for agent in agents + onboarding_agents:
                # Send requests for action
                if agent.wants_action.is_set():
                    live_run.client_io.request_action(agent.get_agent_id())
                    agent.wants_action.clear()
                # Pass updated statuses
                if agent.has_updated_status.is_set():
                    live_run.loop_wrap.execute_coro(self.push_status_update(agent))
                    agent.has_updated_status.clear()
                # clear the message queue for this agent
                live_run.loop_wrap.execute_coro(self._try_send_agent_messages(agent))
            time.sleep(0.1)

    def launch_sending_thread_deprecated(self) -> None:
        """Launch the status sending thread for this pool"""
        # TODO deprecate when status is push based
        self.agent_status_thread = threading.Thread(
            target=self._agent_status_handling_thread, name=f"agent-status-thread"
        )
        self.agent_status_thread.start()

    def shutdown(self) -> None:
        """Shut down and join the status thread"""
        self.is_shutdown = True
        logger.debug(f"Joining send thread")
        if self.agent_status_thread is not None:
            self.agent_status_thread.join()
