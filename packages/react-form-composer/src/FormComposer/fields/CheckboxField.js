/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Errors } from "./Errors";

function CheckboxField({
  field,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  invalid,
  validationErrors,
}) {
  const [lastCheckEvent, setLastCheckEvent] = React.useState(null);
  const [widgetValue, setWidgetValue] = React.useState({});

  const initialValue = initialFormData ? initialFormData[field.name] : {};

  const [invalidField, setInvalidField] = React.useState(false);
  const [errors, setErrors] = React.useState([]);

  function setDefaultWidgetValue() {
    const allItemsNotCheckedValue = Object.fromEntries(
      field.options.map((o) => [o.value, !!o.checked])
    );
    setWidgetValue(allItemsNotCheckedValue);
  }

  function updateFieldData(e, optionValue, checkValue) {
    setLastCheckEvent(e);
    setWidgetValue({ ...widgetValue, ...{ [optionValue]: checkValue } });
  }

  // Effects
  React.useEffect(() => {
    if (Object.keys(widgetValue).length === 0) {
      setDefaultWidgetValue();
    }
  }, []);

  React.useEffect(() => {
    setInvalidField(invalid);
  }, [invalid]);

  React.useEffect(() => {
    setErrors(validationErrors);
  }, [validationErrors]);

  React.useEffect(() => {
    updateFormData(lastCheckEvent, field.name, widgetValue);
  }, [widgetValue]);

  return (
    // bootstrap classes:
    //  - form-check
    //  - is-invalid
    //  - disabled
    //  - form-check-input
    //  - form-check-label

    <>
      {field.options.map((option, index) => {
        const checked = initialFormData
          ? initialValue[option.value]
          : widgetValue[option.value];

        return (
          <div
            key={`option-${field.id}-${index}`}
            className={`
              form-check
              ${field.type} ${disabled ? "disabled" : ""}
              ${invalidField ? "is-invalid" : ""}
            `}
            onClick={(e) => {
              !disabled && updateFieldData(e, option.value, !checked);
              setInvalidField(false);
              setErrors([]);
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
    </>
  );
}

export { CheckboxField };
