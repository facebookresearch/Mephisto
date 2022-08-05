#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from functools import partial
from dataclasses import dataclass, fields
from prometheus_client import Histogram, Gauge, Counter  # type: ignore
from mephisto.data_model.worker import Worker
from mephisto.data_model.agent import Agent, OnboardingAgent
from mephisto.utils.qualifications import worker_is_qualified
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
from mephisto.operations.datatypes import LiveTaskRun, WorkerFailureReasons

from typing import Sequence, Dict, Union, Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.unit import Unit
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.task_run import TaskRun

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


AGENT_DETAILS_COUNT = Counter(
    "agent_details_responses", "Responses to agent details requests", ["response"]
)
AGENT_DETAILS_COUNT.labels(response="not_qualified")
AGENT_DETAILS_COUNT.labels(response="no_available_units")
AGENT_DETAILS_COUNT.labels(response="agent_missing")
AGENT_DETAILS_COUNT.labels(response="reconnection")
AGENT_DETAILS_COUNT.labels(response="assigned")
AGENT_DETAILS_COUNT.labels(response="assigned_onboarding")
ONBOARDING_OUTCOMES = Counter(
    "worker_pool_onboarding_outcomes",
    "Counts of onboarding outcomes as determined by the worker pool",
    ["outcome"],
)
ONBOARDING_OUTCOMES.labels(outcome="launched")
ONBOARDING_OUTCOMES.labels(outcome="passed")
ONBOARDING_OUTCOMES.labels(outcome="failed")
ACTIVE_ONBOARDINGS = Gauge(
    "worker_pool_active_onboardings",
    "Count of active onboardings as determined by the worker pool",
)
EXTERNAL_FUNCTION_LATENCY = Histogram(
    "external_function_latency", "Latency for various user functions", ["function"]
)
EXTERNAL_FUNCTION_LATENCY.labels(function="get_init_data_for_agent")
EXTERNAL_FUNCTION_LATENCY.labels(function="validate_onboarding")
EXTERNAL_FUNCTION_LATENCY.labels(function="get_valid_units_for_worker")
EXTERNAL_FUNCTION_LATENCY.labels(function="filter_units_for_worker")
EXTERNAL_FUNCTION_LATENCY.labels(function="get_screening_unit_data")
EXTERNAL_FUNCTION_LATENCY.labels(function="launch_screening_unit")
EXTERNAL_FUNCTION_LATENCY.labels(function="get_gold_unit_data_for_worker")


@dataclass
class OnboardingInfo:
    crowd_data: Dict[str, Any]
    request_id: str


@dataclass
class AgentDetails:
    """Class containing the information for a newly initialized frontend agent"""

    worker_id: Optional[str] = None
    agent_id: Optional[str] = None
    init_task_data: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None

    def to_dict(self):
        return dict((field.name, getattr(self, field.name)) for field in fields(self))


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
        self.final_onboardings: Dict[str, "OnboardingAgent"] = {}
        # Agent status handling
        self.last_status_check = time.time()

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

    def get_agent_for_id(
        self, agent_id: str
    ) -> Optional[Union["Agent", "OnboardingAgent"]]:
        """Temporary method to get an agent, while API is figured out"""
        if agent_id in self.agents:
            return self.agents[agent_id]
        elif agent_id in self.onboarding_agents:
            return self.onboarding_agents[agent_id]
        elif agent_id in self.final_onboardings:
            logger.debug(
                f"Found agent id {agent_id} in final_onboardings for get_agent_for_id"
            )
            return self.final_onboardings[agent_id]
        return None

    async def register_worker(
        self, crowd_data: Dict[str, Any], request_id: str
    ) -> None:
        """
        First process the worker registration, then hand off for
        registering an agent
        """
        live_run = self.get_live_run()
        loop = live_run.loop_wrap.loop
        crowd_provider = live_run.provider
        is_sandbox = crowd_provider.is_sandbox()
        worker_name = crowd_data["worker_name"]
        if crowd_provider.is_sandbox():
            # TODO(WISH) there are better ways to get rid of this designation
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
            AGENT_DETAILS_COUNT.labels(response="not_qualified").inc()
            live_run.client_io.enqueue_agent_details(
                request_id,
                AgentDetails(
                    failure_reason=WorkerFailureReasons.NOT_QUALIFIED
                ).to_dict(),
            )
        else:
            await self.register_agent(crowd_data, worker, request_id)

    async def _assign_unit_to_agent(
        self,
        crowd_data: Dict[str, Any],
        worker: "Worker",
        request_id: str,
        units: List["Unit"],
    ):
        live_run = self.get_live_run()
        task_run = live_run.task_run
        loop = live_run.loop_wrap.loop
        task_runner = live_run.task_runner
        crowd_provider = live_run.provider

        logger.debug(
            f"Worker {worker.db_id} is being assigned one of {len(units)} units."
        )

        reserved_unit = None
        while len(units) > 0 and reserved_unit is None:
            unit = units.pop(0)
            reserved_unit = task_run.reserve_unit(unit)
        if reserved_unit is None:
            AGENT_DETAILS_COUNT.labels(response="no_available_units").inc()
            live_run.client_io.enqueue_agent_details(
                request_id,
                AgentDetails(
                    worker_id=worker.db_id,
                    failure_reason=WorkerFailureReasons.NO_AVAILABLE_UNITS,
                ).to_dict(),
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
            live_run.client_io.associate_agent_with_registration(
                agent.get_agent_id(),
                request_id,
                crowd_data["agent_registration_id"],
            )
            logger.debug(f"Created agent {agent}, {agent.db_id}.")

            # TODO(#649) this is IO bound
            with EXTERNAL_FUNCTION_LATENCY.labels(
                function="get_init_data_for_agent"
            ).time():
                init_task_data = await loop.run_in_executor(
                    None,
                    partial(
                        task_runner.get_init_data_for_agent,
                        agent,
                    ),
                )

            AGENT_DETAILS_COUNT.labels(response="assigned").inc()
            live_run.client_io.enqueue_agent_details(
                request_id,
                AgentDetails(
                    worker_id=worker.db_id,
                    agent_id=agent.get_agent_id(),
                    init_task_data=init_task_data,
                ).to_dict(),
            )

            self.agents[agent.get_agent_id()] = agent

            # Launch individual tasks
            if unit.unit_index < 0 or not live_run.task_runner.is_concurrent:
                # Run the unit
                live_run.task_runner.execute_unit(
                    unit,
                    agent,
                )
            else:
                assignment = await loop.run_in_executor(None, unit.get_assignment)

                # Set status to waiting
                agent.update_status(AgentState.STATUS_WAITING)

                # See if the concurrent assignment is ready to launch
                logger.debug(f"Attempting to launch {assignment}.")
                agents = await loop.run_in_executor(None, assignment.get_agents)
                if None in agents:
                    return  # need to wait for all agents to be here to launch

                for queried_agent in agents:
                    if queried_agent.get_status() != AgentState.STATUS_WAITING:
                        logger.debug(f"Delaying launch of {assignment}, should retry.")
                        return  # Need to wait for all agents to be waiting to launch

                # Mypy not-null cast
                non_null_agents = [a for a in agents if a is not None]
                # Launch the backend for this assignment
                registered_agents = [
                    self.agents[a.get_agent_id()]
                    for a in non_null_agents
                    if a is not None
                ]

                live_run.task_runner.execute_assignment(assignment, registered_agents)

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
        with EXTERNAL_FUNCTION_LATENCY.labels(function="validate_onboarding").time():
            worker_passed = await loop.run_in_executor(
                None, partial(blueprint.validate_onboarding, worker, onboarding_agent)
            )

        assert blueprint.onboarding_qualification_name is not None
        worker.grant_qualification(
            blueprint.onboarding_qualification_name, int(worker_passed)
        )
        if not worker_passed:
            ONBOARDING_OUTCOMES.labels(outcome="failed").inc()
            worker.grant_qualification(
                blueprint.onboarding_failed_name, int(worker_passed)
            )
            onboarding_agent.update_status(AgentState.STATUS_REJECTED)
            logger.info(f"Onboarding agent {onboarding_id} failed onboarding")
        else:
            ONBOARDING_OUTCOMES.labels(outcome="passed").inc()
            onboarding_agent.update_status(AgentState.STATUS_APPROVED)
            logger.info(
                f"Onboarding agent {onboarding_id} registered out from onboarding"
            )

        # get the list of tentatively valid units
        with EXTERNAL_FUNCTION_LATENCY.labels(
            function="get_valid_units_for_worker"
        ).time():
            units = await loop.run_in_executor(
                None, partial(live_run.task_run.get_valid_units_for_worker, worker)
            )
        with EXTERNAL_FUNCTION_LATENCY.labels(
            function="filter_units_for_worker"
        ).time():
            usable_units = await loop.run_in_executor(
                None,
                partial(live_run.task_runner.filter_units_for_worker, units, worker),
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

        # Assign to a unit
        if len(usable_units) == 0:
            AGENT_DETAILS_COUNT.labels(response="not_qualified").inc()
            live_run.client_io.enqueue_agent_details(
                request_id,
                AgentDetails(
                    failure_reason=WorkerFailureReasons.NOT_QUALIFIED,
                ).to_dict(),
            )
        else:
            await self._assign_unit_to_agent(
                crowd_data, worker, request_id, usable_units
            )

    async def reconnect_agent(self, agent_id: str, request_id: str):
        """When an agent reconnects, find and send the relevant data"""
        live_run = self.get_live_run()
        loop = live_run.loop_wrap.loop
        task_runner = live_run.task_runner
        agent = self.get_agent_for_id(agent_id)
        if agent is None:
            logger.info(
                f"Looking for reconnecting agent {agent_id} but none found locally"
            )
            AGENT_DETAILS_COUNT.labels(response="agent_missing").inc()
            live_run.client_io.enqueue_agent_details(
                request_id,
                AgentDetails(
                    failure_reason=WorkerFailureReasons.TASK_MISSING,
                ).to_dict(),
            )
            return
        worker = agent.get_worker()
        AGENT_DETAILS_COUNT.labels(response="reconnection").inc()
        if isinstance(agent, OnboardingAgent):
            if agent.get_status() == AgentState.STATUS_REJECTED:
                # Rejected agent should get failed response
                live_run.client_io.enqueue_agent_details(
                    request_id,
                    AgentDetails(
                        failure_reason=WorkerFailureReasons.NOT_QUALIFIED
                    ).to_dict(),
                )
            elif agent.get_status() == AgentState.STATUS_DISCONNECT:
                # Disconnected agent should get missing response
                live_run.client_io.enqueue_agent_details(
                    request_id,
                    AgentDetails(
                        failure_reason=WorkerFailureReasons.TASK_MISSING,
                    ).to_dict(),
                )
            else:
                blueprint = live_run.blueprint
                assert (
                    isinstance(blueprint, OnboardingRequired)
                    and blueprint.use_onboarding
                )
                onboard_data = blueprint.get_onboarding_data(worker.db_id)
                live_run.client_io.enqueue_agent_details(
                    request_id,
                    AgentDetails(
                        worker_id=worker.db_id,
                        agent_id=agent.get_agent_id(),
                        init_task_data=onboard_data,
                    ).to_dict(),
                )
        else:
            # TODO(#649) this is IO bound
            with EXTERNAL_FUNCTION_LATENCY.labels(
                function="get_init_data_for_agent"
            ).time():
                init_task_data = await loop.run_in_executor(
                    None,
                    partial(
                        task_runner.get_init_data_for_agent,
                        agent,
                    ),
                )
            live_run.client_io.enqueue_agent_details(
                request_id,
                AgentDetails(
                    worker_id=worker.db_id,
                    agent_id=agent.get_agent_id(),
                    init_task_data=init_task_data,
                ).to_dict(),
            )

    async def register_agent(
        self, crowd_data: Dict[str, Any], worker: "Worker", request_id: str
    ):
        """Process an agent registration packet to register an agent, returning the agent_id"""
        # Process a new agent
        logger.debug(f"Registering agent {crowd_data}, {request_id}")
        live_run = self.get_live_run()
        loop = live_run.loop_wrap.loop
        task_run = live_run.task_run
        agent_registration_id = crowd_data["agent_registration_id"]

        # get the list of tentatively valid units
        with EXTERNAL_FUNCTION_LATENCY.labels(
            function="get_valid_units_for_worker"
        ).time():
            units = task_run.get_valid_units_for_worker(worker)

        if len(units) == 0:
            AGENT_DETAILS_COUNT.labels(response="no_available_units").inc()
            live_run.client_io.enqueue_agent_details(
                request_id,
                AgentDetails(
                    worker_id=worker.db_id,
                    failure_reason=WorkerFailureReasons.NO_AVAILABLE_UNITS,
                ).to_dict(),
            )
            logger.debug(
                f"agent_registration_id {agent_registration_id}, had no valid units."
            )
            return
        with EXTERNAL_FUNCTION_LATENCY.labels(
            function="filter_units_for_worker"
        ).time():
            units = await loop.run_in_executor(
                None,
                partial(live_run.task_runner.filter_units_for_worker, units, worker),
            )
        # If there's onboarding, see if this worker has already been disqualified
        blueprint = live_run.blueprint
        if isinstance(blueprint, OnboardingRequired) and blueprint.use_onboarding:
            qual_name = blueprint.onboarding_qualification_name
            assert (
                qual_name is not None
            ), "Cannot be using onboarding and have a null qual"
            if worker.is_disqualified(qual_name):
                AGENT_DETAILS_COUNT.labels(response="not_qualified").inc()
                live_run.client_io.enqueue_agent_details(
                    request_id,
                    AgentDetails(
                        worker_id=worker.db_id,
                        failure_reason=WorkerFailureReasons.NOT_QUALIFIED,
                    ).to_dict(),
                )
                logger.debug(
                    f"Worker {worker.db_id} is already disqualified by onboarding "
                    f"qual {qual_name}."
                )
                return
            elif not worker.is_qualified(qual_name):
                # Send a packet with onboarding information
                onboard_data = blueprint.get_onboarding_data(worker.db_id)
                onboard_agent = OnboardingAgent.new(self.db, worker, task_run)
                live_run.client_io.associate_agent_with_registration(
                    onboard_agent.get_agent_id(),
                    request_id,
                    crowd_data["agent_registration_id"],
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

                ONBOARDING_OUTCOMES.labels(outcome="launched").inc()
                ACTIVE_ONBOARDINGS.inc()
                AGENT_DETAILS_COUNT.labels(response="assigned_onboarding").inc()
                live_run.client_io.enqueue_agent_details(
                    request_id,
                    AgentDetails(
                        worker_id=worker.db_id,
                        agent_id=onboard_id,
                        init_task_data=onboard_data,
                    ).to_dict(),
                )
                logger.info(
                    f"{worker} is starting onboarding thread with "
                    f"onboarding {onboard_agent}."
                )

                async def cleanup_onboarding():
                    onboarding_agent = self.onboarding_agents[onboard_id]
                    del self.onboarding_agents[onboard_id]
                    self.final_onboardings[onboard_id] = onboarding_agent
                    del self.onboarding_infos[onboard_id]
                    ACTIVE_ONBOARDINGS.dec()

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
                with EXTERNAL_FUNCTION_LATENCY.labels(
                    function="get_screening_unit_data"
                ).time():
                    screening_data = await loop.run_in_executor(
                        None, blueprint.get_screening_unit_data
                    )
                if screening_data is not None:
                    launcher = live_run.task_launcher
                    assert (
                        launcher is not None
                    ), "LiveTaskRun must have launcher to use screening tasks"
                    with EXTERNAL_FUNCTION_LATENCY.labels(
                        function="launch_screening_unit"
                    ).time():
                        screen_unit = await loop.run_in_executor(
                            None,
                            partial(
                                launcher.launch_screening_unit,
                                screening_data,
                            ),
                        )
                    units = [screen_unit]
                else:
                    AGENT_DETAILS_COUNT.labels(response="no_available_units").inc()
                    live_run.client_io.enqueue_agent_details(
                        request_id,
                        AgentDetails(
                            worker_id=worker.db_id,
                            failure_reason=WorkerFailureReasons.NO_AVAILABLE_UNITS,
                        ).to_dict(),
                    )
                    logger.debug(
                        f"No screening units left for {agent_registration_id}."
                    )
                    return
        if isinstance(blueprint, UseGoldUnit) and blueprint.use_golds:
            if blueprint.should_produce_gold_for_worker(worker):
                with EXTERNAL_FUNCTION_LATENCY.labels(
                    function="get_gold_unit_data_for_worker"
                ).time():
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
                    AGENT_DETAILS_COUNT.labels(response="no_available_units").inc()
                    live_run.client_io.enqueue_agent_details(
                        request_id,
                        AgentDetails(
                            worker_id=worker.db_id,
                            failure_reason=WorkerFailureReasons.NO_AVAILABLE_UNITS,
                        ).to_dict(),
                    )
                    logger.debug(f"No gold units left for {agent_registration_id}...")
                    return

        # Not onboarding, so just register directly
        await self._assign_unit_to_agent(crowd_data, worker, request_id, units)

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
        live_run.client_io.send_status_update(agent.get_agent_id(), status)

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
            if agent_id in self.final_onboardings:
                # no longer tracking this onboarding
                continue
            agent = self.get_agent_for_id(agent_id)
            if agent is None:
                # no longer tracking agent
                continue
            db_status = agent.get_status()
            if status != db_status:
                if status == AgentState.STATUS_COMPLETED:
                    # Frontend agent completed but hasn't confirmed yet
                    continue
                if status != AgentState.STATUS_DISCONNECT:
                    # Stale or reconnect, send a status update
                    live_run.loop_wrap.execute_coro(self.push_status_update(agent))
                    continue  # Only DISCONNECT can be marked remotely, rest are mismatch (except STATUS_COMPLETED)
                agent.update_status(status)
        pass

    def disconnect_active_agents(self) -> None:
        """
        Under a forced shutdown, set the status of all current agents
        to disconnected to clear their running tasks
        """
        for agent in self.agents.values():
            if agent.get_status() not in AgentState.complete():
                agent.update_status(AgentState.STATUS_DISCONNECT)
        for onboarding_agent in self.onboarding_agents.values():
            onboarding_agent.update_status(AgentState.STATUS_DISCONNECT)

    def shutdown(self) -> None:
        """Mark shut down. Handle resource cleanup if necessary"""
        self.is_shutdown = True
