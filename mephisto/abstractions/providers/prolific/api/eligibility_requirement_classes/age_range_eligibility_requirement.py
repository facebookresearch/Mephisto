from .base_eligibility_requirement import BaseEligibilityRequirement


class AgeRangeEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """
    prolific_cls_name = 'web.eligibility.models.AgeRangeEligibilityRequirement'

    def __init__(self, min_age: int, max_age: int):
        self.min_age = min_age
        self.max_age = max_age

    def to_prolific_dict(self) -> dict:
        prolific_dict = super().to_prolific_dict()
        prolific_dict['query'] = dict(id=None)
        return prolific_dict
