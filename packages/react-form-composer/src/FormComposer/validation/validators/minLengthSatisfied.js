/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  MIN_LENGTH_ERROR_MESSAGE_KEY,
  MIN_LENGTH_ITEMS_ERROR_MESSAGE_KEY,
  validationErrorMessagesByName,
} from "../errorMessages";

/**
 * Check if minimum length of value is not less than specified value
 * @param {object} field FormComposer field
 * @param {any} value HTML element
 * @param {number} minLength integer number of minimum length
 * @return {string|null} error message or `null`
 */
export default function minLengthSatisfied(field, value, minLength) {
  let valueLength = 0;
  const _minLength = Math.floor(minLength);
  let errorMessage = validationErrorMessagesByName[
    MIN_LENGTH_ERROR_MESSAGE_KEY
  ](_minLength);

  if (["input", "textarea", "email"].includes(field.type)) {
    const _value = (value || "").trim();
    valueLength = _value.length;
  }

  if (field.type === "checkbox") {
    const _value = value || {};
    valueLength = Object.entries(_value).filter(([k, v]) => v === true).length;
    errorMessage = validationErrorMessagesByName[
      MIN_LENGTH_ITEMS_ERROR_MESSAGE_KEY
    ](_minLength);
  }

  if (field.type === "select" && field.multiple === true) {
    const _value = value || [];
    valueLength = _value.length;
    errorMessage = validationErrorMessagesByName[
      MIN_LENGTH_ITEMS_ERROR_MESSAGE_KEY
    ](_minLength);
  }

  if (valueLength < _minLength) {
    return errorMessage;
  }

  return null;
}
