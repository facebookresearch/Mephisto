import { REQUIRED_ERROR_MESSAGE_KEY, validationErrorMessagesByName } from "../errorMessages";

/**
 * Check if value is not empty
 * @param {object} field FormComposer field
 * @param {HTMLElement} formFieldElement HTML element
 * @param {boolean} required requiredness
 * @return {string|null} error message or `null`
 */
export default function fieldIsRequired(field, formFieldElement, required) {
  if (!required) {
    return;
  }

  let value = formFieldElement.value;
  if (typeof value === "string") {
    value = (value || "").trim();
  }

  const fieldIsEmpty = ["", null, undefined].includes(value);

  if (fieldIsEmpty) {
    return validationErrorMessagesByName[REQUIRED_ERROR_MESSAGE_KEY];
  }

  return null;
}

