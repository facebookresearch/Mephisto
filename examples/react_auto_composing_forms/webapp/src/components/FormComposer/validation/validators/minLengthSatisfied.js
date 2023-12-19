import { MIN_LENGTH_ERROR_MESSAGE_KEY, validationErrorMessagesByName } from "../errorMessages";

/**
 * Check if minimum length of value is not less than specified value
 * @param {object} field FormComposer field
 * @param {HTMLElement} formFieldElement HTML element
 * @param {number} minLength integer number of minimum length
 * @return {string|null} error message or `null`
 */
export default function minLengthSatisfied(field, formFieldElement, minLength) {
  if (["input", "textarea"].includes(field.type)) {
    const value = (formFieldElement.value || "").trim();

    const _minLength = Math.floor(minLength);
    if (value.length < _minLength) {
      return validationErrorMessagesByName[MIN_LENGTH_ERROR_MESSAGE_KEY](_minLength);
    }
  }

  return null;
}
