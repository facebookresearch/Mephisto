#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Union

from .base_model import BaseModel


class BonusPayments(BaseModel):
    """
    More about Bonuses:
        https://docs.prolific.co/docs/api-docs/public/#tag/Bonuses
    """

    amount: Union[int, float]
    fees: Union[int, float]
    id: str
    study: str
    total_amount: Union[int, float]
    vat: Union[int, float]

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
        },
    }

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id}"
