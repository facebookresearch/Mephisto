/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import $ from "jquery";
import { FieldType } from "../constants";
import { REQUIRED_ERROR_MESSAGE_KEY } from "./errorMessages";
import { validatorFunctionsByConfigName } from "./validatorLookup";

/**
 * Check if field's validators include `required` validator
 * @param {object} field FormComposer field
 * @return {boolean} whether field is required
 */
export function checkFieldRequiredness(field) {
  const validators = field.validators || {};
  const requredValue = validators[REQUIRED_ERROR_MESSAGE_KEY];
  return requredValue && requredValue === true;
}

/**
 * Check if field is visible in DOM
 * @param {object} field FormComposer field
 * @return {boolean} whether field is visible
 */
export function fieldIsVisible(field) {
  const $htmlFieldElement = $(`[name="${field.name}"]`);
  // All fields have same wrapper that contains label, etc.
  const $htmlFieldElementWrapper = $htmlFieldElement.closest(".field");

  // In case if field is invisible and field wrapper has `hidden` class.
  // Otherwise, we will select even collapsed sections and other unexpected blocks
  const htmlFieldElementIsVisible =
    $htmlFieldElement && $htmlFieldElement.is(":visible");
  const htmlFieldElementWrapperIsHidden = $htmlFieldElementWrapper.hasClass(
    "hidden"
  );

  if (htmlFieldElementIsVisible && !htmlFieldElementWrapperIsHidden) {
    return true;
  }

  return false;
}

/**
 * Validate Form-elements
 * @param {object} formFieldsValues Form state data
 * @param {object} fields FormComposer fields
 * @param {module} customValidators optional module with custom validation functions
 * @return {object} invalid FormComposer fields
 */
export function validateFormFields(formFieldsValues, fields, customValidators) {
  const invalidFormFields = {};

  let _validatorFunctionsByConfigName = validatorFunctionsByConfigName;
  // Update default validators with provided by user
  if (customValidators) {
    _validatorFunctionsByConfigName = {
      ..._validatorFunctionsByConfigName,
      ...customValidators,
    };
  }

  Object.entries(formFieldsValues).forEach(([fieldName, fieldValue]) => {
    const field = fields[fieldName];

    if (!field) {
      return;
    }

    // No need to validate fields with type `hidden`, send them as is
    if (field.type === FieldType.HIDDEN) {
      return;
    }

    // If HTML-element of a field is invisible, do not validate it
    if (!fieldIsVisible(field)) {
      return;
    }

    const fieldValidators = field.validators || {};

    Object.entries(fieldValidators).forEach((validator) => {
      const [validatorName, validatorArguments] = validator;

      // Arguments for validator can be a list or simple type value.
      // We always pass arguments as positional arguments after 2 first mandatory arguments,
      // such as `field` and `formFieldElement`.
      // So we wrap an argumet with a list if it is not a list
      let _validatorArguments = validatorArguments;
      if (!(validatorArguments instanceof Array)) {
        _validatorArguments = [validatorArguments];
      }

      if (!_validatorFunctionsByConfigName.hasOwnProperty(validatorName)) {
        console.warn(
          `You tried to validate field "${field.name}" with validator "${validatorName}". ` +
            `"FormComposer" does not support this validator, so we just ignore it`
        );
        return;
      }

      const validatorFunction = _validatorFunctionsByConfigName[validatorName];
      const validationResult = validatorFunction(
        field,
        fieldValue,
        ..._validatorArguments
      );

      if (validationResult) {
        invalidFormFields[field.name] = [
          ...(invalidFormFields[field.name] || []),
          validationResult,
        ];
      }
    });
  });

  return invalidFormFields;
}

/**
 * Prepare Form Data in Mephisto format before submitting (JSON in correct fields and attachments)
 * @param {object} formFieldsValues Form state data
 * @param {object} fields FormComposer fields
 * @return {FormData} FormData you already can submit
 */
export function prepareFormDataForSubmit(formFieldsValues, fields) {
  let finalData = {};

  // Exclude invisible fields
  Object.keys(formFieldsValues).forEach((fieldName) => {
    const field = fields[fieldName];
    const fieldHasHiddenType = field.type === FieldType.HIDDEN;

    if (!fieldHasHiddenType && !fieldIsVisible(field)) {
      return;
    }

    finalData[fieldName] = formFieldsValues[fieldName];
  });

  // Append JSON data
  const formData = new FormData();
  formData.append("final_data", finalData);
  formData.append("final_string_data", JSON.stringify(finalData));

  // Append files in Form Data next to JSON data
  const fileInputs = document.querySelectorAll("input[type='file']");
  fileInputs.forEach((input) => {
    if (!finalData[input.name]) {
      return;
    }

    if (input.files?.length) {
      Object.values(input.files).forEach((file) => {
        formData.append(input.name, file, file.name);
      });
    }
  });

  return formData;
}
