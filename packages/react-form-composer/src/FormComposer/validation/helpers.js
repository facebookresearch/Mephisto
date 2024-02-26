/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
 * Validate Form-elements
 * @param {HTMLElement[]} formFieldsValues HTML elements
 * @param {object} fields FormComposer fields
 * @return {object} invalid FormComposer fields
 */
export function validateFormFields(formFieldsValues, fields) {
  const invalidFormFields = {};

  Object.entries(formFieldsValues).forEach(([fieldName, fieldValue]) => {
    const field = fields[fieldName];

    if (!field) {
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

      if (!validatorFunctionsByConfigName.hasOwnProperty(validatorName)) {
        console.warn(
          `You tried to validate field "${field.name}" with validator "${validatorName}". ` +
            `"FormComposer" does not support this validator, so we just ignore it`
        );
        return;
      }

      const validatorFunction = validatorFunctionsByConfigName[validatorName];
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
