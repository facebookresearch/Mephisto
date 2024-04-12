# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .base_eligibility_requirement import BaseEligibilityRequirement


class CustomBlacklistEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.com/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    name = "CustomBlacklistEligibilityRequirement"
    prolific_cls_name = f"web.eligibility.models.{name}"

    def __init__(self, black_list: List[str]):
        self.black_list = black_list
