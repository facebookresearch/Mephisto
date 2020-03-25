#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.requester import Requester
from mephisto.providers.mock.provider_type import PROVIDER_TYPE
from mephisto.core.argparse_parser import str2bool

from typing import Optional, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun
    from argparse import _ArgumentGroup as ArgumentGroup

MOCK_BUDGET = 100000.0


class MockRequester(Requester):
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    def __init__(self, db: "MephistoDB", db_id: str):
        super().__init__(db, db_id)
        # TODO any additional init as is necessary once
        # a mock DB exists, make register actually work
        self.registered = self.requester_name == "test_requester"

    def register(self, args: Optional[Dict[str, str]] = None) -> None:
        """Mock requesters don't actually register credentials"""
        if args is not None:
            if args.get("force_fail") is True:
                raise Exception("Forced failure test exception was set")
        else:
            self.registered = True

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        Add mock registration arguments to the argument group.
        """
        super(MockRequester, cls).add_args_to_group(group)

        group.description = """
            MockRequester: Arguments for mock requester add special
            control and test functionality.
        """
        group.add_argument(
            "--force-fail",
            dest="force_fail",
            type=str2bool,
            default=False,
            help="Trigger a failed registration",
        )
        return

    def is_registered(self) -> bool:
        """Return the registration status"""
        return self.registered

    def get_available_budget(self) -> float:
        """MockRequesters have $100000 to spend"""
        return MOCK_BUDGET

    def is_sandbox(self) -> bool:
        """MockRequesters are for testing only, and are thus treated as sandbox"""
        return True

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return MockRequester._register_requester(db, requester_name, PROVIDER_TYPE)
