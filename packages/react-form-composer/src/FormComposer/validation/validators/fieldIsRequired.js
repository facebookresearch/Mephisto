/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  REQUIRED_ERROR_MESSAGE_KEY,
  validationErrorMessagesByName,
} from "../errorMessages";

/**
 * Check if value is not empty
 * @param {object} field FormComposer field
 * @param {any} value HTML element
 * @param {boolean} required requiredness
 * @return {string|null} error message or `null`
 */
export default function fieldIsRequired(field, value, required) {
  if (!required) {
    return null;
  }

  let _value = value;
  if (typeof _value === "string") {
    _value = (_value || "").trim();
  } else if (field.type === "checkbox") {
    const numberOfSelectedValues = Object.values(value).filter(
      (v) => v === true
    ).length;
    _value = numberOfSelectedValues ? value : null;
  } else if (field.type === "select" && field.multiple === true) {
    _value = (value || []).length > 0 ? value : null;
  }

  const fieldIsEmpty = ["", null, undefined].includes(_value);

  if (fieldIsEmpty) {
    return validationErrorMessagesByName[REQUIRED_ERROR_MESSAGE_KEY];
  }

  return null;
}
