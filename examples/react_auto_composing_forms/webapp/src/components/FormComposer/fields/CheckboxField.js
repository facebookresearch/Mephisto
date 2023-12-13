/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function CheckboxField({
  field, updateFormData, disabled, initialFormData, isInReviewState, isInvalid, validationErrors,
}) {
  const [lastCheckEvent, setLastCheckEvent] = React.useState(null);
  const [widgetValue, setWidgetValue] = React.useState({});

  const initialValue = initialFormData ? initialFormData[field.name] : {};

  function setDefaultWidgetValue() {
    const allItemsNotCheckedValue = Object.fromEntries(
      field.options.map(o => [o.value, !!o.checked])
    );
    setWidgetValue(allItemsNotCheckedValue);
  }

  function updateFieldData(e, optionValue, checkValue) {
    setLastCheckEvent(e);
    setWidgetValue({ ...widgetValue, ...{[optionValue]: checkValue }});
  }

  React.useEffect(() => {
    if (Object.keys(widgetValue).length === 0) {
      setDefaultWidgetValue();
    }
  }, []);

  React.useEffect(() => {
    updateFormData(lastCheckEvent, field.name, widgetValue);
  }, [widgetValue]);

  return (<>
    {field.options.map(( option, index ) => {
      const checked = (
        initialFormData
          ? initialValue[option.value]
          : widgetValue[option.value]
      );

      return (
        <div
          key={`option-${field.id}-${index}`}
          className={`
            form-check
            ${field.type} ${disabled ? "disabled" : ""}
            ${isInvalid ? "is-invalid" : ""}
          `}
          onClick={(e) => !disabled && updateFieldData(e, option.value, !checked)}
        >
          <span
            className={`form-check-input ${checked ? "checked" : ""}`}
            id={`${field.id}-${index}`}
            style={field.style}
          />
          <span className={`form-check-label`}>
            {option.label}
          </span>
        </div>
      );
    })}

    {validationErrors && (
      <div className={`invalid-feedback`}>
        {validationErrors.join("\n")}
      </div>
    )}
  </>);
}

export { CheckboxField };
