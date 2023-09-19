#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from decimal import Decimal
from typing import Dict
from typing import Union

from .base_model import BaseModel


class WorkspaceBalance(BaseModel):
    """
    More about Workspaces:
        https://docs.prolific.co/docs/api-docs/public/#tag/Workspaces
    """

    currency_code: str
    total_balance: Union[Decimal, float, int]
    balance_breakdown: Dict[str, Union[Decimal, float, int]]
    available_balance: Union[Decimal, float, int]
    available_balance_breakdown: Dict[str, Union[Decimal, float, int]]

    schema = {
        "type": "object",
        "properties": {
            "currency_code": {"type": "string"},
            "total_balance": {"type": "number"},
            "balance_breakdown": {
                "type": "object",
                "properties": {
                    "rewards": {"type": "number"},
                    "fees": {"type": "number"},
                    "vat": {"type": "number"},
                },
            },
            "available_balance": {"type": "number"},
            "available_balance_breakdown": {
                "type": "object",
                "properties": {
                    "rewards": {"type": "number"},
                    "fees": {"type": "number"},
                    "vat": {"type": "number"},
                },
            },
        },
    }

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.total_balance} {self.currency_code}"
