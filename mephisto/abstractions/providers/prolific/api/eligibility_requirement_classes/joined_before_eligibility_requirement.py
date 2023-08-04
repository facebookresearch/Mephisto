from .base_eligibility_requirement import BaseEligibilityRequirement


class JoinedBeforeEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    name = "JoinedBeforeEligibilityRequirement"
    prolific_cls_name = f"web.eligibility.models.{name}"

    def __init__(self, joined_before: str):
        self.joined_before = joined_before
