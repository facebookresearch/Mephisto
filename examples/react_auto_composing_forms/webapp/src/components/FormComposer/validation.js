export const REQUIRED_VALIDATOR_NAME = "required";
export const MIN_LENGTH_VALIDATOR_NAME = "minLength";

export const validationErrorMessagesByName = {
  [REQUIRED_VALIDATOR_NAME]: "Field is required.",
  [MIN_LENGTH_VALIDATOR_NAME]: (n) => `Min length of value must be not less then ${n}.`,
}

export function required(field, formFieldElement, required) {
  if (!required) {
    return;
  }

  const fieldIsEmpty = ["", null, undefined].includes(formFieldElement.value);

  if (fieldIsEmpty) {
    return validationErrorMessagesByName[REQUIRED_VALIDATOR_NAME];
  }

  return null;
}

export function minLength(field, formFieldElement, minLength) {
  if (["input", "textarea"].includes(field.type)) {
    const value = formFieldElement.value || "";

    if (value.length < minLength) {
      return validationErrorMessagesByName[MIN_LENGTH_VALIDATOR_NAME](minLength);
    }
  }

  return null
}

export const validatorsByName = {
  [REQUIRED_VALIDATOR_NAME]: required,
  [MIN_LENGTH_VALIDATOR_NAME]: minLength,
}

export function fieldIsRequired(field) {
  const validators = field.validators || {};
  const requredValue = validators[REQUIRED_VALIDATOR_NAME];
  return requredValue && requredValue.includes(true);
}
