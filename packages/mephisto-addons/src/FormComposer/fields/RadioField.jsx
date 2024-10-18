/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { runCustomTrigger } from "../utils";
import { Errors } from "./Errors.jsx";
import "./RadioField.css";

const DEFAULT_VALUE = "";

function RadioField({
  field,
  formData,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  invalid,
  validationErrors,
  formFields,
  customTriggers,
  cleanErrorsOnChange,
}) {
  const [value, setValue] = React.useState(DEFAULT_VALUE);

  const [invalidField, setInvalidField] = React.useState(false);
  const [errors, setErrors] = React.useState([]);

  // Methods
  function _runCustomTrigger(triggerName) {
    if (inReviewState) {
      return;
    }

    runCustomTrigger(
      field.triggers,
      triggerName,
      customTriggers,
      formData,
      updateFormData,
      field,
      value,
      formFields
    );
  }

  function onClick(e) {
    _runCustomTrigger("onClick");
  }

  function onChange(e, optionValue) {
    updateFormData(field.name, optionValue, e);
    _runCustomTrigger("onChange");
  }

  // --- Effects ---
  React.useEffect(() => {
    setInvalidField(invalid);
  }, [invalid]);

  React.useEffect(() => {
    setErrors(validationErrors);
  }, [validationErrors]);

  // Value in formData is updated
  React.useEffect(() => {
    setValue(formData[field.name] || DEFAULT_VALUE);
  }, [formData[field.name]]);

  return (
    // bootstrap classes:
    //  - form-check
    //  - is-invalid
    //  - disabled
    //  - form-check-input
    //  - form-check-label

    <div className={`fc-radio-field`} name={field.name} onClick={onClick}>
      {field.options.map((option, index) => {
        const checked = value === option.value;

        return (
          <div
            key={`option-${field.id}-${index}`}
            className={`
              form-check
              ${field.type}
              ${disabled ? "disabled" : ""}
              ${invalidField ? "is-invalid" : ""}
            `}
            onClick={(e) => {
              !disabled && onChange(e, option.value);
              if (cleanErrorsOnChange) {
                setInvalidField(false);
                setErrors([]);
              }
            }}
          >
            <span
              className={`form-check-input ${checked ? "checked" : ""}`}
              id={`${field.id}-${index}`}
              style={field.style}
            />
            <span className={`form-check-label`}>{option.label}</span>
          </div>
        );
      })}

      <Errors messages={errors} />
    </div>
  );
}

export { RadioField };
