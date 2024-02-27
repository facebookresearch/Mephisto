/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  FILE_EXTENSION_ERROR_MESSAGE_KEY,
  validationErrorMessagesByName,
} from "../errorMessages";

/**
 * Check if file has correct extension
 * @param {object} field FormComposer field
 * @param {any} value HTML element
 * @param {string[]} extensions Array with extensions
 * @return {string|null} error message or `null`
 */
export default function fileExtensionSatisfied(field, value, ...extensions) {
  if (field.type !== "file") {
    return null;
  }

  if (!value) {
    return null;
  }

  const fileName = (value.name || "").trim();
  const _extensions = extensions.map((e) =>
    e.toLowerCase().replaceAll(".", "")
  );

  const fileExtension = fileName.split(".").pop().toLowerCase();
  const fileHasCorrectExtension = _extensions.includes(fileExtension);

  if (!fileHasCorrectExtension) {
    const extensionsString = _extensions.join(", ");
    return validationErrorMessagesByName[FILE_EXTENSION_ERROR_MESSAGE_KEY](
      extensionsString,
      fileExtension
    );
  }

  return null;
}
