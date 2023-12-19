import { REGEXP_ERROR_MESSAGE_KEY, validationErrorMessagesByName } from "../errorMessages";

/**
 * Check if string-value matches RegExp
 * @param {object} field FormComposer field
 * @param {HTMLElement} formFieldElement HTML element
 * @param {string} regexp RegExp as string
 * @param {string} regexpFlags JavaScript RegExp flags
 * @return {string|null} error message or `null`
 */
export default function regexpSatisfied(field, formFieldElement, regexp, regexpFlags) {
  if (["input", "textarea"].includes(field.type)) {
    const value = (formFieldElement.value || "").trim();

    const _regexpParams = regexpFlags || "igm"
    const _regexp = new RegExp(regexp, _regexpParams);

    if (!_regexp.test(value)) {
      return validationErrorMessagesByName[REGEXP_ERROR_MESSAGE_KEY];
    }
  }

  return null;
}

