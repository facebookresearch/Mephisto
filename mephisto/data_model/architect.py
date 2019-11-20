#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.database import MephistoDB

class Architect(ABC):
    """
    Provides methods for setting up a server somewhere and deploying tasks
    onto that server.
    """

    def __init__(self, db: 'MephistoDB', opts: Dict[str, str], task_run: 'TaskRun', build_dir_root: str):
        """
        Initialize this architect with whatever options are provided given
        get_extra_options. Parse whatever additional options may be required
        for the specific task_run.

        Also set up any required database/memory into the MephistoDB so that
        this data can be stored long-term.
        """
        raise NotImplementedError()

    @staticmethod
    def get_extra_options() -> Dict[str, str]:
        """
        Defines options that are potentially usable for this server location
        """
        # TODO update to a format that will be rendererable on the frontend.
        return {}

    def prepare(self) -> str:
        """
        Produce the server files that will be deployed to the server
        """
        raise NotImplementedError()

    def deploy(self) -> str:
        """
        Launch the server, and push the task files to the server. Return
        the server URL
        """
        raise NotImplementedError()

    def cleanup(self) -> None:
        """
        Remove any files that were used for the deployment process that
        no longer need to be kept track of now that the task has
        been launched.
        """
        raise NotImplementedError()

    def shutdown(self) -> None:
        """
        Shut down the server launched by this Surveyor, as stored
        in the db.
        """
        raise NotImplementedError()
