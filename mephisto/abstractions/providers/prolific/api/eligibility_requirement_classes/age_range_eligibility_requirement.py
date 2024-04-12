# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.providers.prolific.api.constants import (
    ELIGIBILITY_REQUIREMENT_AGE_RANGE_QUESTION_ID,
)
from .base_eligibility_requirement import BaseEligibilityRequirement


class AgeRangeEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.com/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    name = "AgeRangeEligibilityRequirement"
    prolific_cls_name = f"web.eligibility.models.{name}"

    def __init__(self, min_age: int, max_age: int):
        self.min_age = min_age
        self.max_age = max_age

    def to_prolific_dict(self) -> dict:
        prolific_dict = super().to_prolific_dict()

        # HACK: Hardcoded Question IDs (Prolific doesn't have a better way for now)
        # [Depends on Prolific] Make this dynamic as soon as possible
        prolific_dict["query"] = dict(id=ELIGIBILITY_REQUIREMENT_AGE_RANGE_QUESTION_ID)

        return prolific_dict
