/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  REGEXP_ERROR_MESSAGE_KEY,
  validationErrorMessagesByName,
} from "../errorMessages";

/**
 * Check if string-value matches RegExp
 * @param {object} field FormComposer field
 * @param {any} value HTML element
 * @param {string} regexp RegExp as string
 * @param {string} regexpFlags JavaScript RegExp flags
 * @return {string|null} error message or `null`
 */
export default function regexpSatisfied(field, value, regexp, regexpFlags) {
  if (["input", "textarea", "email"].includes(field.type)) {
    const _value = (value || "").trim();

    const _regexpParams = regexpFlags || "igm";
    const _regexp = new RegExp(regexp, _regexpParams);

    if (!_regexp.test(_value)) {
      return validationErrorMessagesByName[REGEXP_ERROR_MESSAGE_KEY];
    }
  }

  return null;
}
