#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from mephisto.data_model.requester import Requester
from mephisto.data_model.requester import RequesterArgs
from .provider_type import PROVIDER_TYPE
from .surge_ai_utils import check_balance
from .surge_ai_utils import check_credentials

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.surge_ai.surge_ai_datastore import SurgeAIDatastore
    from omegaconf import DictConfig


@dataclass
class SurgeAIRequesterArgs(RequesterArgs):
    name: str = field(
        default="SURGE_AI_REQUESTER",
        metadata={
            "help": "Name for the requester in the Mephisto DB.",
            "required": True,
        },
    )
    force_fail: bool = field(
        default=False, metadata={"help": "Trigger a failed registration"}
    )


class SurgeAIRequester(Requester):
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    ArgsClass = SurgeAIRequesterArgs

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "SurgeAIDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)

    def register(self, args: Optional["DictConfig"] = None) -> None:
        if args is not None:
            if args.get("force_fail") is True:
                raise Exception("Forced failure test exception was set")
        else:
            self.datastore.set_requester_registered(self.db_id, True)

    def is_registered(self) -> bool:
        """Return whether this requester has registered yet"""
        return check_credentials()

    def get_available_budget(self) -> float:
        return check_balance()

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return SurgeAIRequester._register_requester(db, requester_name, PROVIDER_TYPE)
