# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_eligibility_requirement import BaseEligibilityRequirement


class ParticipantGroupEligibilityRequirement(BaseEligibilityRequirement):
    """
    Details https://docs.prolific.com/docs/api-docs/public/#tag/Requirements/Requirements-object
    """

    name = "ParticipantGroupEligibilityRequirement"
    prolific_cls_name = f"web.eligibility.models.{name}"

    def __init__(self, id: str):
        self.id = id
        self.value = True

    def to_prolific_dict(self) -> dict:
        prolific_dict = dict(
            _cls=self.prolific_cls_name,
            attributes=[
                dict(
                    id=self.id,
                    value=self.value,
                )
            ],
        )
        return prolific_dict
