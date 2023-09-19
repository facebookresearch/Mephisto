from typing import List

from .base_eligibility_requirement import BaseEligibilityRequirement


class CustomBlacklistEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    name = "CustomBlacklistEligibilityRequirement"
    prolific_cls_name = f"web.eligibility.models.{name}"

    def __init__(self, black_list: List[str]):
        self.black_list = black_list
