import inspect

from omegaconf import ListConfig


class BaseEligibilityRequirement:
    """
    Base class to create Prolific Eligibility Requirement.
    Usage:
        1. Create a class:
            class AgeRangeEligibilityRequirement(BaseEligibilityRequirement):
                prolific_cls_name = 'web.eligibility.models.AgeRangeEligibilityRequirement'

                def __init__(self, min_value: int, max_value: int):
                    self.min_value = min_value
                    self.max_value = max_value

        2. Add requirements in hydra config under `provider` section:
              provider:
                prolific_eligibility_requirements:
                  - name: 'AgeRangeEligibilityRequirement'
                    min_value: 10
                    max_value: 20

        3. In the code all these requirements will be converted to the Prolific format
        (see mephisto.abstractions.providers.prolific.prolific_utils._get_eligibility_requirements)
    """

    prolific_cls_name = None

    @classmethod
    def params(cls):
        params = list(inspect.signature(cls.__init__).parameters.keys())
        params.remove("self")
        return params

    def to_prolific_dict(self) -> dict:
        prolific_dict = dict(
            _cls=self.prolific_cls_name,
            attributes=[],
        )
        for param_name in self.params():
            param_value = getattr(self, param_name, None)

            if isinstance(param_value, ListConfig):
                param_value = list(param_value)

            if param_value:
                prolific_dict["attributes"].append(
                    dict(
                        name=param_name,
                        value=param_value,
                    )
                )
        return prolific_dict

    def __str__(self) -> str:
        _str = self.__class__.__name__
        for param_name in self.params():
            _str += f" {param_name}={getattr(self, param_name, None)}"
        return _str

    def __repr__(self) -> str:
        return self.__str__()
