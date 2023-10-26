# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from .base_eligibility_requirement import BaseEligibilityRequirement


class ApprovalNumbersEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    name = "ApprovalNumbersEligibilityRequirement"
    prolific_cls_name = f"web.eligibility.models.{name}"

    def __init__(
        self,
        minimum_approvals: Optional[int] = None,
        maximum_approvals: Optional[int] = None,
    ):
        self.minimum_approvals = minimum_approvals
        self.maximum_approvals = maximum_approvals
