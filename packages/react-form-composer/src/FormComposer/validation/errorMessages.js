/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export const FILE_EXTENSION_ERROR_MESSAGE_KEY = "file-extension";
export const MAX_LENGTH_ERROR_MESSAGE_KEY = "max-length";
export const MAX_LENGTH_ITEMS_ERROR_MESSAGE_KEY = "max-length-items";
export const MIN_LENGTH_ERROR_MESSAGE_KEY = "min-length";
export const MIN_LENGTH_ITEMS_ERROR_MESSAGE_KEY = "min-length-items";
export const REGEXP_ERROR_MESSAGE_KEY = "regexp";
export const REQUIRED_ERROR_MESSAGE_KEY = "required";

export const validationErrorMessagesByName = {
  [FILE_EXTENSION_ERROR_MESSAGE_KEY]: (t, a) =>
    `File type should be: ${t}. You attached: ${a}.`,
  [MAX_LENGTH_ERROR_MESSAGE_KEY]: (n) =>
    `Value should be no more than ${n} characters.`,
  [MAX_LENGTH_ITEMS_ERROR_MESSAGE_KEY]: (n) =>
    `Should have at most ${n} items selected.`,
  [MIN_LENGTH_ERROR_MESSAGE_KEY]: (n) =>
    `Value should be at least ${n} characters long.`,
  [MIN_LENGTH_ITEMS_ERROR_MESSAGE_KEY]: (n) =>
    `Should have at least ${n} items selected.`,
  [REGEXP_ERROR_MESSAGE_KEY]: "Incorrectly formatted input.",
  [REQUIRED_ERROR_MESSAGE_KEY]: "This field is required.",
};
