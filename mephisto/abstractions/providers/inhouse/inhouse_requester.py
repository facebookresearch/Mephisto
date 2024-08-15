#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.abstractions.providers.inhouse.provider_type import PROVIDER_TYPE
from mephisto.data_model.requester import Requester
from mephisto.data_model.requester import RequesterArgs
from mephisto.utils.logger_core import get_logger

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.inhouse.inhouse_datastore import InhouseDatastore

DEFAULT_AVAILABLE_BUDGET = 100000.0
DEFAULT_IS_REGISTERED = True

logger = get_logger(name=__name__)


@dataclass
class InhouseRequesterArgs(RequesterArgs):
    name: str = field(
        default="inhouse",
        metadata={
            "help": "Name for the requester in the Mephisto DB.",
            "required": False,
        },
    )


class InhouseRequester(Requester):
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    ArgsClass = InhouseRequesterArgs

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "InhouseDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)

    @property
    def log_prefix(self) -> str:
        return "[Inhouse Requester] "

    def register(self, args: Optional[InhouseRequesterArgs] = None) -> None:
        logger.debug(f"{self.log_prefix}Registering Inhouse requester")
        return None

    def is_registered(self) -> bool:
        """Return whether this requester has registered yet"""
        logger.debug(
            f"{self.log_prefix}Check if Inhouse requester is registered: {DEFAULT_IS_REGISTERED}"
        )
        return DEFAULT_IS_REGISTERED

    def get_available_budget(self) -> float:
        logger.debug(f"{self.log_prefix}Check if Inhouse requester is registered: true")
        return DEFAULT_AVAILABLE_BUDGET

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return InhouseRequester._register_requester(db, requester_name, PROVIDER_TYPE)
