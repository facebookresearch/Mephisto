from typing import List

from .base_eligibility_requirement import BaseEligibilityRequirement

CUSTOM_BLACKLIST_ELIGIBILITY_REQUIREMENT = 'CustomBlacklistEligibilityRequirement'


class CustomBlacklistEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """
    prolific_cls_name = f'web.eligibility.models.{CUSTOM_BLACKLIST_ELIGIBILITY_REQUIREMENT}'

    def __init__(self, black_list: List[str]):
        self.black_list = black_list
