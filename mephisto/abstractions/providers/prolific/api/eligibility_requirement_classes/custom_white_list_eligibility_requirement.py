# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

from .base_eligibility_requirement import BaseEligibilityRequirement


class CustomWhitelistEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.com/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    name = "CustomWhitelistEligibilityRequirement"
    prolific_cls_name = f"web.eligibility.models.{name}"

    def __init__(self, white_list: List[str]):
        self.white_list = white_list
