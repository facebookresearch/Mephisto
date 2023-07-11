from .base_eligibility_requirement import BaseEligibilityRequirement

PARTICIPANT_GROUP_ELIGIBILITY_REQUIREMENT = 'ParticipantGroupEligibilityRequirement'


class ParticipantGroupEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.co/docs/api-docs/public/#tag/Requirements/Requirements-object
    """
    prolific_cls_name = f'web.eligibility.models.{PARTICIPANT_GROUP_ELIGIBILITY_REQUIREMENT}'

    def __init__(self, id: str):
        self.id = id
        self.value = True

    def to_prolific_dict(self) -> dict:
        prolific_dict = dict(
            _cls=self.prolific_cls_name,
            attributes=[dict(
                id=self.id,
                value=self.value,
            )],
        )
        return prolific_dict
