#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractstaticmethod
from mephisto.data_model.database import MephistoDB
from mephisto.data_model.agent import AGENT_STATUSES
from mephisto.core.utils import get_crowd_provider_from_type
from typing import List, Optional, Tuple, Dict


class Worker(ABC):
    """
    This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
    """

    def __init__(self, db: MephistoDB, db_id: str):
        self.db_id: str = db_id
        self.db: MephistoDB = db
        row = db.get_worker(db_id)
        self.provider_type = row["provider_type"]
        self.db_status = row["status"]
        # TODO Do we want any other attributes here?

    def __new__(cls, db: MephistoDB, db_id: str) -> Unit:
        """
        The new method is overridden to be able to automatically generate
        the expected Worker class without needing to specifically find it
        for a given db_id. As such it is impossible to create a base Worker
        as you will instead be returned the correct Worker class according to
        the crowdprovider associated with this Worker.
        """
        if cls == Worker:
            # We are trying to construct a Worker, find what type to use and
            # create that instead
            row = db.get_worker(db_id)
            correct_class = get_crowd_provider_from_type(
                row["provider_type"]
            ).WorkerClass
            return super().__new__(correct_class, db, db_id)
        else:
            # We are constructing another instance directly
            return super().__new__(cls, db, db_id)

    # TODO make getters for helpful worker statistics
    # TODO add worker qualification tracking

    # TODO make abstract helpers for bonusing? and blocking

    def get_agents(self, status: Optional[str] = None) -> List[Agent]:
        """
        Get the list of agents that this worker was responsible for, by the given status
        if needed
        """
        assert status is None or status in AGENT_STATUSES, "Invalid agent status"
        return self.db.find_agents(worker_id=self.db_id, status=status)

    @staticmethod
    def _register_worker(db: MephistoDB, worker_id: str, provider_type: str) -> Worker:
        """
        Create an entry for this worker in the database
        """
        db_id = db.new_worker(worker_id, provider_type)
        return Worker(db, db_id)

    @abstractstaticmethod
    def new(db: MephistoDB, worker_id: str) -> Worker:
        """
        Create a new worker attached to the given identifier, assuming it doesn't already
        exist in the database.

        Implementation should return the result of _register_worker when sure the worker
        can be successfully created to have it put into the db.
        """
        raise NotImplementedError()
