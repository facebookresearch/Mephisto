from .base_eligibility_requirement import BaseEligibilityRequirement


class JoinedBeforeEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """
    prolific_cls_name = 'web.eligibility.models.JoinedBeforeEligibilityRequirement'

    def __init__(self, joined_before: str):
        self.joined_before = joined_before
