/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { runCustomTrigger } from "../utils";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors";

function TextareaField({
  field,
  formData,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  invalid,
  validationErrors,
  customTriggers,
}) {
  const [widgetValue, setWidgetValue] = React.useState("");

  const initialValue = initialFormData ? initialFormData[field.name] : "";

  const [invalidField, setInvalidField] = React.useState(false);
  const [errors, setErrors] = React.useState([]);

  // Methods
  function _runCustomTrigger(triggerName) {
    runCustomTrigger(
      field.triggers,
      triggerName,
      customTriggers,
      formData,
      updateFormData,
      field,
      widgetValue
    );
  }

  function onBlur(e) {
    _runCustomTrigger("onBlur");
  }

  function onFocus(e) {
    _runCustomTrigger("onFocus");
  }

  function onClick(e) {
    _runCustomTrigger("onClick");
  }

  // Effects
  React.useEffect(() => {
    setInvalidField(invalid);
  }, [invalid]);

  React.useEffect(() => {
    setErrors(validationErrors);
  }, [validationErrors]);

  React.useEffect(() => {
    _runCustomTrigger("onChange");
  }, [widgetValue]);

  return (
    // bootstrap classes:
    //  - form-control
    //  - is-invalid

    <>
      <textarea
        className={`
          form-control
          ${invalidField ? "is-invalid" : ""}
        `}
        id={field.id}
        name={field.name}
        placeholder={field.placeholder}
        style={field.style}
        required={checkFieldRequiredness(field)}
        defaultValue={initialValue}
        onChange={(e) => {
          !disabled && updateFormData(field.name, e.target.value, e);
          setWidgetValue(e.target.value);
          setInvalidField(false);
          setErrors([]);
        }}
        onBlur={onBlur}
        onFocus={onFocus}
        onClick={onClick}
        disabled={disabled}
      />

      <Errors messages={errors} />
    </>
  );
}

export { TextareaField };
