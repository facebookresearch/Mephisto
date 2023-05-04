from .base_eligibility_requirement import BaseEligibilityRequirement


class ApprovalRateEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """
    prolific_cls_name = 'web.eligibility.models.ApprovalRateEligibilityRequirement'

    def __init__(self, minimum_approval_rate: int, maximum_approval_rate: int):
        self.minimum_approval_rate = minimum_approval_rate
        self.maximum_approval_rate = maximum_approval_rate
