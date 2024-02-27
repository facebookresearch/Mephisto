/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  MAX_LENGTH_ERROR_MESSAGE_KEY,
  MAX_LENGTH_ITEMS_ERROR_MESSAGE_KEY,
  validationErrorMessagesByName,
} from "../errorMessages";

/**
 * Check if maximum length of value is not bigger than specified value
 * @param {object} field FormComposer field
 * @param {any} value HTML element
 * @param {number} maxLength integer number of maximum length
 * @return {string|null} error message or `null`
 */
export default function maxLengthSatisfied(field, value, maxLength) {
  let valueLength = 0;
  const _maxLength = Math.floor(maxLength);
  let errorMessage = validationErrorMessagesByName[
    MAX_LENGTH_ERROR_MESSAGE_KEY
  ](_maxLength);

  if (["input", "textarea", "email"].includes(field.type)) {
    const _value = (value || "").trim();
    valueLength = _value.length;
  }

  if (field.type === "checkbox") {
    const _value = value || {};
    valueLength = Object.entries(_value).filter(([k, v]) => v === true).length;
    errorMessage = validationErrorMessagesByName[
      MAX_LENGTH_ITEMS_ERROR_MESSAGE_KEY
    ](_maxLength);
  }

  if (field.type === "select" && field.multiple === true) {
    const _value = value || [];
    valueLength = _value.length;
    errorMessage = validationErrorMessagesByName[
      MAX_LENGTH_ITEMS_ERROR_MESSAGE_KEY
    ](_maxLength);
  }

  if (valueLength > _maxLength) {
    return errorMessage;
  }

  return null;
}
