from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from mephisto.data_model.unit import Unit


ValidationFuncType = Callable[[Any, Optional[Any]], bool]


def _simple_comparing(worker_value: Any, correct_value: Optional[Any]) -> bool:
    if correct_value is None:
        # Just skip if there's no value, we do not validate this field at all
        return True

    return worker_value == correct_value


def _validate_name_first(worker_value: Any, correct_value: Optional[Any]) -> bool:
    return _simple_comparing(worker_value, correct_value)


def _validate_name_last(worker_value: Any, correct_value: Optional[Any]) -> bool:
    return _simple_comparing(worker_value, correct_value)


def _validate_email(worker_value: Any, correct_value: Optional[Any]) -> bool:
    return _simple_comparing(worker_value, correct_value)


def _validate_country(worker_value: Any, correct_value: Optional[Any]) -> bool:
    return _simple_comparing(worker_value, correct_value)


def _validate_language(worker_value: Any, correct_value: Optional[Any]) -> bool:
    return _simple_comparing(worker_value, correct_value)


def _validate_bio(worker_value: Any, correct_value: Optional[Any]) -> bool:
    # Custom more complicated logic
    if len(worker_value) < 10:
        return False

    if "Gold" not in worker_value:
        return False

    if "Bad" in worker_value:
        return False

    return True


FIELD_VALIDATOR_MAPPINGS = {
    "name_first": _validate_name_first,
    "name_last": _validate_name_last,
    "email": _validate_email,
    "country": _validate_country,
    "language": _validate_language,
    "bio": _validate_bio,
}


def validate_gold_unit(unit: "Unit") -> bool:
    agent = unit.get_assigned_agent()
    data = agent.state.get_data()

    worker_answeres = data["outputs"]

    expecting_answers: dict = data["inputs"]["expecting_answers"]

    validated_fields: List[bool] = []

    for fieldname, correct_value in expecting_answers.items():
        # No correct value set for this field, they pass validation
        if correct_value is None:
            validated_fields.append(True)
            continue

        # No validation function set for this field, they pass validation
        validation_func: ValidationFuncType = FIELD_VALIDATOR_MAPPINGS.get(fieldname)
        if not validation_func:
            validated_fields.append(True)
            continue

        # No worker answer for this field, they fail validation
        worker_value = worker_answeres.get(fieldname)
        if not worker_value:
            validated_fields.append(False)
            continue

        validation_result = validation_func(worker_value, correct_value)
        validated_fields.append(validation_result)

    return all(validated_fields)
