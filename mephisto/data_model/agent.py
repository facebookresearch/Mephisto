#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations

import os
import threading
from queue import Queue
from uuid import uuid4
from prometheus_client import Gauge  # type: ignore

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.worker import Worker
from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedABCMeta,
    MephistoDataModelComponentMixin,
)
from mephisto.data_model.exceptions import (
    AgentReturnedError,
    AgentDisconnectedError,
    AgentTimeoutError,
    AgentShutdownError,
)

from typing import List, Optional, Tuple, Mapping, Dict, Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.assignment import Assignment
    from mephisto.abstractions.database import MephistoDB
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.task import Task
    from mephisto.data_model.task_run import TaskRun
    from mephisto.operations.datatypes import LiveTaskRun

from mephisto.utils.logger_core import get_logger, warn_once

logger = get_logger(name=__name__)


ACTIVE_AGENT_STATUSES = Gauge(
    "active_agent_statuses",
    "Tracking of all units current statuses",
    ["status", "agent_type"],
)
for status in AgentState.valid():
    ACTIVE_AGENT_STATUSES.labels(status=status, agent_type="main")
    ACTIVE_AGENT_STATUSES.labels(status=status, agent_type="onboarding")
ACTIVE_WORKERS = Gauge(
    "active_workers",
    "Tracking of active workers and how many agents they have",
    ["worker_id", "agent_type"],
)


# TODO(CLEAN) can probably refactor out some kind of AgentBase
class Agent(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedABCMeta):
    """
    This class encompasses a worker as they are working on an individual assignment.
    It maintains details for the current task at hand such as start and end time,
    connection status, etc.
    """

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct Agent and data model access via ...Agent(db, id) was "
                "now deprecated in favor of calling Agent.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_agent(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["agent_id"]
        self.db_status: str = row["status"]
        self.worker_id: str = row["worker_id"]
        self.unit_id: str = row["unit_id"]
        self.task_type: str = row["task_type"]
        self.provider_type: str = row["provider_type"]
        self.pending_actions: "Queue[Dict[str, Any]]" = Queue()
        self.has_live_update = threading.Event()
        self.has_live_update.clear()
        self.assignment_id: str = row["assignment_id"]
        self.task_run_id: str = row["task_run_id"]
        self.task_id: str = row["task_id"]
        self.did_submit = threading.Event()
        self.is_shutdown = False

        # Deferred loading of related entities
        self._worker: Optional["Worker"] = None
        self._unit: Optional["Unit"] = None
        self._assignment: Optional["Assignment"] = None
        self._task_run: Optional["TaskRun"] = None
        self._task: Optional["Task"] = None

        # Related entity set by a live run
        self._associated_live_run: Optional["LiveTaskRun"] = None

        # Follow-up initialization is deferred
        self._state = None  # type: ignore

    @property
    def state(self) -> "AgentState":
        if self._state is None:
            self._state = AgentState(self)  # type: ignore
        return cast("AgentState", self._state)

    def __new__(
        cls,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ) -> "Agent":
        """
        The new method is overridden to be able to automatically generate
        the expected Agent class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Agent
        as you will instead be returned the correct Agent class according to
        the crowdprovider associated with this Agent.
        """
        from mephisto.operations.registry import get_crowd_provider_from_type

        if cls == Agent:
            # We are trying to construct a Agent, find what type to use and
            # create that instead
            if row is None:
                row = db.get_agent(db_id)
            assert row is not None, f"Given db_id {db_id} did not exist in given db"
            correct_class = get_crowd_provider_from_type(
                row["provider_type"]
            ).AgentClass
            return super().__new__(correct_class)
        else:
            # We are constructing another instance directly
            return super().__new__(cls)

    def set_live_run(self, live_run: "LiveTaskRun") -> None:
        """Set an associated live run for this agent"""
        self._associated_live_run = live_run

    def get_live_run(self) -> "LiveTaskRun":
        """Return the associated live run for this agent. Throw if not set"""
        if self._associated_live_run is None:
            raise AssertionError(
                "Should not be getting the live run, not set for given agent"
            )
        return self._associated_live_run

    def get_agent_id(self) -> str:
        """Return this agent's id"""
        return self.db_id

    def get_worker(self) -> Worker:
        """
        Return the worker that is using this agent for a task
        """
        if self._worker is None:
            self._worker = Worker.get(self.db, self.worker_id)
        return self._worker

    def get_unit(self) -> "Unit":
        """
        Return the Unit that this agent is working on.
        """
        if self._unit is None:
            from mephisto.data_model.unit import Unit

            self._unit = Unit.get(self.db, self.unit_id)
        return self._unit

    def get_assignment(self) -> "Assignment":
        """Return the assignment this agent is working on"""
        if self._assignment is None:
            if self._unit is not None:
                self._assignment = self._unit.get_assignment()
            else:
                from mephisto.data_model.assignment import Assignment

                self._assignment = Assignment.get(self.db, self.assignment_id)
        return self._assignment

    def get_task_run(self) -> "TaskRun":
        """Return the TaskRun this agent is working within"""
        if self._task_run is None:
            if self._unit is not None:
                self._task_run = self._unit.get_task_run()
            elif self._assignment is not None:
                self._task_run = self._assignment.get_task_run()
            else:
                from mephisto.data_model.task_run import TaskRun

                self._task_run = TaskRun.get(self.db, self.task_run_id)
        return self._task_run

    def get_task(self) -> "Task":
        """Return the Task this agent is working within"""
        if self._task is None:
            if self._unit is not None:
                self._task = self._unit.get_task()
            elif self._assignment is not None:
                self._task = self._assignment.get_task()
            elif self._task_run is not None:
                self._task = self._task_run.get_task()
            else:
                from mephisto.data_model.task import Task

                self._task = Task.get(self.db, self.task_id)
        return self._task

    def get_data_dir(self) -> str:
        """
        Return the directory to be storing any agent state for
        this agent into
        """
        assignment_dir = self.get_assignment().get_data_dir()
        return os.path.join(assignment_dir, self.db_id)

    def update_status(self, new_status: str) -> None:
        """Update the database status of this agent, and
        possibly send a message to the frontend agent informing
        them of this update"""
        if self.db_status == new_status:
            return  # Noop, this is already the case
        logger.debug(f"Updating {self} to {new_status}")
        if self.db_status in AgentState.complete():
            logger.info(f"Updating {self} from final status to {new_status}")

        old_status = self.db_status
        self.db.update_agent(self.db_id, status=new_status)
        self.db_status = new_status
        if self._associated_live_run is not None:
            live_run = self.get_live_run()
            live_run.loop_wrap.execute_coro(
                live_run.worker_pool.push_status_update(self)
            )
        if new_status in [
            AgentState.STATUS_RETURNED,
            AgentState.STATUS_DISCONNECT,
            AgentState.STATUS_TIMEOUT,
        ]:
            # Disconnect statuses should free any pending acts
            self.has_live_update.set()
            self.did_submit.set()
            if old_status == AgentState.STATUS_WAITING:
                # Waiting agents' unit can be reassigned, as no work
                # has been done yet.
                unit = self.get_unit()
                logger.debug(f"Clearing {self} from {unit} for update to {new_status}")
                unit.clear_assigned_agent()

        # Metrics changes
        ACTIVE_AGENT_STATUSES.labels(status=old_status, agent_type="main").dec()
        ACTIVE_AGENT_STATUSES.labels(status=new_status, agent_type="main").inc()
        if (
            old_status not in AgentState.complete()
            and new_status in AgentState.complete()
        ):
            ACTIVE_WORKERS.labels(worker_id=self.worker_id, agent_type="main").dec()

    @staticmethod
    def _register_agent(
        db: "MephistoDB", worker: Worker, unit: "Unit", provider_type: str
    ) -> "Agent":
        """
        Create this agent in the mephisto db with the correct setup
        """
        unit._mark_agent_assignment()
        db_id = db.new_agent(
            worker.db_id,
            unit.db_id,
            unit.task_id,
            unit.task_run_id,
            unit.assignment_id,
            unit.task_type,
            provider_type,
        )
        a = Agent.get(db, db_id)
        ACTIVE_AGENT_STATUSES.labels(
            status=AgentState.STATUS_NONE, agent_type="main"
        ).inc()
        ACTIVE_WORKERS.labels(worker_id=worker.db_id, agent_type="main").inc()
        logger.debug(f"Registered new agent {a} for {unit}.")
        a.update_status(AgentState.STATUS_ACCEPTED)
        return a

    # Specialized child cases may need to implement the following

    @classmethod
    def new_from_provider_data(
        cls,
        db: "MephistoDB",
        worker: Worker,
        unit: "Unit",
        provider_data: Dict[str, Any],
    ) -> "Agent":
        """
        Wrapper around the new method that allows registering additional
        bookkeeping information from a crowd provider for this agent
        """
        agent = cls.new(db, worker, unit)
        unit.worker_id = worker.db_id
        agent._unit = unit
        return agent

    def observe(self, live_update: "Dict[str, Any]") -> None:
        """
        Pass the observed information to the AgentState, then
        queue the information to be pushed to the user
        """
        if live_update.get("update_id") is None:
            live_update["update_id"] = str(uuid4())
        self.state.update_data(live_update)

        if self._associated_live_run is not None:
            live_run = self.get_live_run()
            live_run.client_io.send_live_update(self.get_agent_id(), live_update)

    def get_live_update(
        self, timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Request information from the Agent's frontend. If non-blocking,
        (timeout is None) should return None if no actions are ready
        to be returned.
        """
        if self.pending_actions.empty():
            if timeout is None or timeout == 0:
                return None
            self.has_live_update.wait(timeout)

        if self.pending_actions.empty():
            if self.is_shutdown:
                raise AgentShutdownError(self.db_id)
            # various disconnect cases
            status = self.get_status()
            if status == AgentState.STATUS_DISCONNECT:
                raise AgentDisconnectedError(self.db_id)
            elif status == AgentState.STATUS_RETURNED:
                raise AgentReturnedError(self.db_id)
            self.update_status(AgentState.STATUS_TIMEOUT)
            raise AgentTimeoutError(timeout, self.db_id)
        assert (
            not self.pending_actions.empty()
        ), "has_live_update released without an action!"

        act = self.pending_actions.get()

        if self.pending_actions.empty():
            self.has_live_update.clear()
        self.state.update_data(act)
        return act

    def act(self, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Request information from the Agent's frontend. If non-blocking,
        (timeout is None) should return None if no actions are ready
        to be returned.
        """
        warn_once(
            "As of Mephisto 1.0 Agent.act is being deprecated in favor of Agent.get_live_update. "
            "This functionality will no longer work in 1.1"
        )
        return self.get_live_update(timeout)

    def await_submit(self, timeout: Optional[int] = None) -> bool:
        """Blocking wait for this agent to submit their task"""
        if timeout is not None:
            self.did_submit.wait(timeout=timeout)
        return self.did_submit.is_set()

    def handle_submit(self, submit_data: Dict[str, Any]) -> None:
        """Handle final submission for an onboarding agent, with the given data"""
        self.did_submit.set()
        self.state.update_submit(submit_data)

    def get_status(self) -> str:
        """Get the status of this agent in their work on their unit"""
        if self.db_status not in AgentState.complete():
            row = self.db.get_agent(self.db_id)
            if row["status"] != self.db_status:
                if row["status"] in [
                    AgentState.STATUS_RETURNED,
                    AgentState.STATUS_DISCONNECT,
                ]:
                    # Disconnect statuses should free any pending acts
                    self.has_live_update.set()
                if self._associated_live_run is not None:
                    live_run = self.get_live_run()
                    live_run.loop_wrap.execute_coro(
                        live_run.worker_pool.push_status_update(self)
                    )
            self.db_status = row["status"]
        return self.db_status

    def shutdown(self) -> None:
        """
        Force the given agent to end any polling threads and throw an AgentShutdownError
        from any acts called on it, ensuring tasks using this agent can be cleaned up.
        """
        logger.debug(f"{self} is shutting down")
        self.has_live_update.set()
        self.is_shutdown = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id}, {self.db_status})"

    # Children classes should implement the following methods

    def approve_work(self) -> None:
        """Approve the work done on this agent's specific Unit"""
        raise NotImplementedError()

    def soft_reject_work(self) -> None:
        """
        Pay a worker for attempted work, but mark it as below the
        quality bar for this assignment
        """
        # TODO(OWN) extend this method to assign a soft block
        # qualification automatically if a threshold of
        # soft rejects as a proportion of total accepts
        # is exceeded
        self.approve_work()
        self.update_status(AgentState.STATUS_SOFT_REJECTED)

    def reject_work(self, reason) -> None:
        """Reject the work done on this agent's specific Unit"""
        raise NotImplementedError()

    def mark_done(self) -> None:
        """
        Take any required step with the crowd_provider to ensure that
        the worker can submit their work and be marked as complete via
        a call to get_status
        """
        raise NotImplementedError()

    @staticmethod
    def new(db: "MephistoDB", worker: Worker, unit: "Unit") -> "Agent":
        """
        Create an agent for this worker to be used for work on the given Unit.

        Implementation should return the result of _register_agent when sure the agent
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()


class OnboardingAgent(
    MephistoDataModelComponentMixin, metaclass=MephistoDBBackedABCMeta
):
    """
    Onboarding agents are a special extension of agents used
    in tasks that have a separate onboarding step. These agents
    are designed to work without being linked to an explicit
    unit, and instead are tied to the task run and task name.


    Blueprints that require OnboardingAgents should implement an
    OnboardingAgentState (to process the special task), and their
    TaskRunners should have a run_onboarding and cleanup_onboarding
    method.
    """

    DISPLAY_PREFIX = "onboarding_"

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        if not _used_new_call:
            raise AssertionError(
                "Direct OnboardingAgent and data model access via OnboardingAgent(db, id) is "
                "now deprecated in favor of calling OnboardingAgent.get(db, id). "
            )
        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_onboarding_agent(db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["onboarding_agent_id"]
        self.db_status: str = row["status"]
        self.worker_id: str = row["worker_id"]
        self.task_type: str = row["task_type"]
        self.pending_actions: "Queue[Dict[str, Any]]" = Queue()
        self.has_live_update = threading.Event()
        self.has_live_update.clear()
        self.task_run_id: str = row["task_run_id"]
        self.task_id: str = row["task_id"]
        self.did_submit = threading.Event()
        self.is_shutdown = False

        # Deferred loading of related entities
        self._worker: Optional["Worker"] = None
        self._task_run: Optional["TaskRun"] = None
        self._task: Optional["Task"] = None

        # Related entity set by a live run
        self._associated_live_run: Optional["LiveTaskRun"] = None

        # Follow-up initialization
        self.state = AgentState(self)  # type: ignore

    def get_agent_id(self) -> str:
        """Return an id to use for onboarding agent requests"""
        return f"{self.DISPLAY_PREFIX}{self.db_id}"

    def set_live_run(self, live_run: "LiveTaskRun") -> None:
        """Set an associated live run for this agent"""
        self._associated_live_run = live_run

    def get_live_run(self) -> "LiveTaskRun":
        """Return the associated live run for this agent. Throw if not set"""
        if self._associated_live_run is None:
            raise AssertionError(
                "Should not be getting the live run, not set for given agent"
            )
        return self._associated_live_run

    @classmethod
    def is_onboarding_id(cls, agent_id: str) -> bool:
        """return if the given id is for an onboarding agent"""
        return agent_id.startswith(cls.DISPLAY_PREFIX)

    @classmethod
    def get_db_id_from_agent_id(cls, agent_id: str) -> str:
        """Extract the db_id for an onboarding_agent"""
        assert agent_id.startswith(
            cls.DISPLAY_PREFIX
        ), f"Provided id {agent_id} is not an onboarding_id"
        return agent_id[len(cls.DISPLAY_PREFIX) :]

    def get_worker(self) -> Worker:
        """
        Return the worker that is using this agent for a task
        """
        if self._worker is None:
            self._worker = Worker.get(self.db, self.worker_id)
        return self._worker

    def get_task_run(self) -> "TaskRun":
        """Return the TaskRun this agent is working within"""
        if self._task_run is None:
            from mephisto.data_model.task_run import TaskRun

            self._task_run = TaskRun.get(self.db, self.task_run_id)
        return self._task_run

    def get_task(self) -> "Task":
        """Return the Task this agent is working within"""
        if self._task is None:
            if self._task_run is not None:
                self._task = self._task_run.get_task()
            else:
                from mephisto.data_model.task import Task

                self._task = Task.get(self.db, self.task_id)
        return self._task

    def get_data_dir(self) -> str:
        """
        Return the directory to be storing any agent state for
        this agent into
        """
        task_run_dir = self.get_task_run().get_run_dir()
        return os.path.join(task_run_dir, "onboarding", self.get_agent_id())

    def update_status(self, new_status: str) -> None:
        """Update the database status of this agent, and
        possibly send a message to the frontend agent informing
        them of this update"""
        if self.db_status == new_status:
            return  # Noop, this is already the case

        logger.debug(f"Updating {self} to {new_status}")
        if self.db_status in AgentState.complete():
            logger.info(f"Updating {self} from final status to {new_status}")

        old_status = self.db_status
        self.db.update_onboarding_agent(self.db_id, status=new_status)
        self.db_status = new_status
        if self._associated_live_run is not None:
            if new_status not in [
                AgentState.STATUS_APPROVED,
                AgentState.STATUS_REJECTED,
            ]:
                live_run = self.get_live_run()
                live_run.loop_wrap.execute_coro(
                    live_run.worker_pool.push_status_update(self)
                )
        if new_status in [AgentState.STATUS_RETURNED, AgentState.STATUS_DISCONNECT]:
            # Disconnect statuses should free any pending acts
            self.has_live_update.set()
            self.did_submit.set()

        # Metrics changes
        ACTIVE_AGENT_STATUSES.labels(status=old_status, agent_type="onboarding").dec()
        ACTIVE_AGENT_STATUSES.labels(status=new_status, agent_type="onboarding").inc()
        if (
            old_status not in AgentState.complete()
            and new_status in AgentState.complete()
        ):
            ACTIVE_WORKERS.labels(
                worker_id=self.worker_id, agent_type="onboarding"
            ).dec()

    def observe(self, live_update: "Dict[str, Any]") -> None:
        """
        Pass the observed information to the AgentState, then
        queue the information to be pushed to the user
        """
        if live_update.get("update_id") is None:
            live_update["update_id"] = str(uuid4())
        self.state.update_data(live_update)

        if self._associated_live_run is not None:
            live_run = self.get_live_run()
            live_run.client_io.send_live_update(self.get_agent_id(), live_update)

    def get_live_update(
        self, timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Request information from the Agent's frontend. If non-blocking,
        (timeout is None) should return None if no actions are ready
        to be returned.
        """
        if self.pending_actions.empty():
            if timeout is None or timeout == 0:
                return None
            self.has_live_update.wait(timeout)

        if self.pending_actions.empty():
            # various disconnect cases
            if self.is_shutdown:
                raise AgentShutdownError(self.db_id)
            status = self.get_status()
            if status == AgentState.STATUS_DISCONNECT:
                raise AgentDisconnectedError(self.db_id)
            elif status == AgentState.STATUS_RETURNED:
                raise AgentReturnedError(self.db_id)
            self.update_status(AgentState.STATUS_TIMEOUT)
            raise AgentTimeoutError(timeout, self.db_id)
        assert (
            not self.pending_actions.empty()
        ), "has_live_update released without an action!"

        act = self.pending_actions.get()

        if self.pending_actions.empty():
            self.has_live_update.clear()
        self.state.update_data(act)
        return act

    def act(self, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Request information from the Agent's frontend. If non-blocking,
        (timeout is None) should return None if no actions are ready
        to be returned.
        """
        warn_once(
            "As of Mephisto 1.0 Agent.act is being deprecated in favor of Agent.get_live_update. "
            "This functionality will no longer work in 1.1"
        )
        return self.get_live_update(timeout)

    def await_submit(self, timeout: Optional[int] = None) -> bool:
        """Blocking wait for this agent to submit their task"""
        if timeout is not None:
            self.did_submit.wait(timeout=timeout)
        return self.did_submit.is_set()

    def handle_submit(self, submit_data: Dict[str, Any]) -> None:
        """Handle final submission for an onboarding agent, with the given data"""
        self.did_submit.set()
        self.state.update_submit(submit_data)

    def get_status(self) -> str:
        """Get the status of this agent in their work on their unit"""
        if self.db_status not in AgentState.complete():
            row = self.db.get_onboarding_agent(self.db_id)
            if row["status"] != self.db_status:
                if row["status"] in [
                    AgentState.STATUS_RETURNED,
                    AgentState.STATUS_DISCONNECT,
                ]:
                    # Disconnect statuses should free any pending acts
                    self.has_live_update.set()
                if row["status"] not in [
                    AgentState.STATUS_APPROVED,
                    AgentState.STATUS_REJECTED,
                ]:
                    if self._associated_live_run is not None:
                        live_run = self.get_live_run()
                        live_run.loop_wrap.execute_coro(
                            live_run.worker_pool.push_status_update(self)
                        )
            self.db_status = row["status"]
        return self.db_status

    def shutdown(self) -> None:
        """
        Force the given agent to end any polling threads and throw an AgentShutdownError
        from any acts called on it, ensuring tasks using this agent can be cleaned up.
        """
        logger.debug(f"{self} is shutting down")
        self.has_live_update.set()
        self.is_shutdown = True

    @staticmethod
    def new(db: "MephistoDB", worker: Worker, task_run: "TaskRun") -> "OnboardingAgent":
        """
        Create an OnboardingAgent for a worker to use as part of a task run
        """
        db_id = db.new_onboarding_agent(
            worker.db_id, task_run.task_id, task_run.db_id, task_run.task_type
        )
        a = OnboardingAgent.get(db, db_id)
        ACTIVE_AGENT_STATUSES.labels(
            status=AgentState.STATUS_NONE, agent_type="onboarding"
        ).inc()
        ACTIVE_WORKERS.labels(worker_id=worker.db_id, agent_type="onboarding").inc()
        logger.debug(f"Registered new {a} for worker {worker}.")
        return a

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.db_id})"
