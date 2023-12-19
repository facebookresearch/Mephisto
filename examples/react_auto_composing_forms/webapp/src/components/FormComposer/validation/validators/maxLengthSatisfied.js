import { MAX_LENGTH_ERROR_MESSAGE_KEY, validationErrorMessagesByName } from "../errorMessages";

/**
 * Check if maximum length of value is not bigger than specified value
 * @param {object} field FormComposer field
 * @param {HTMLElement} formFieldElement HTML element
 * @param {number} maxLength integer number of maximum length
 * @return {string|null} error message or `null`
 */
export default function maxLengthSatisfied(field, formFieldElement, maxLength) {
  if (["input", "textarea"].includes(field.type)) {
    const value = (formFieldElement.value || "").trim();

    const _maxLength = Math.floor(maxLength);
    if (value.length > _maxLength) {
      return validationErrorMessagesByName[MAX_LENGTH_ERROR_MESSAGE_KEY](_maxLength);
    }
  }

  return null;
}
