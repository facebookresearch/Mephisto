/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import "bootstrap";
import "bootstrap-select";
import $ from "jquery";
import React from "react";
import { runCustomTrigger } from "../utils";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors";

function SelectField({
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
}) {
  const defaultValue = field.multiple ? [] : "";
  const [value, setValue] = React.useState(defaultValue);

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
      formFields,
    );
  }

  function onChange(e, fieldName) {
    let fieldValue = e.target.value;
    if (field.multiple) {
      fieldValue = Array.from(
        e.target.selectedOptions,
        (option) => option.value
      );
    }

    updateFormData(fieldName, fieldValue, e);
    _runCustomTrigger("onChange");
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

  // --- Effects ---
  React.useEffect(() => {
    // Enable plugin
    $(`.selectpicker.select-${field.name}`).selectpicker();
  }, []);

  React.useEffect(() => {
    if (invalid) {
      $(`.bootstrap-select.select-${field.name}`).addClass("is-invalid");
    } else {
      $(`.bootstrap-select.select-${field.name}`).removeClass("is-invalid");
    }

    setInvalidField(invalid);
  }, [invalid]);

  React.useEffect(() => {
    if (invalidField) {
      $(`.bootstrap-select.select-${field.name}`).addClass("is-invalid");
    } else {
      $(`.bootstrap-select.select-${field.name}`).removeClass("is-invalid");
    }
  }, [invalidField]);

  React.useEffect(() => {
    setErrors(validationErrors);
  }, [validationErrors]);

  React.useEffect(() => {
    // Refresh plugin after value was changed
    const $fieldElement = $(`.selectpicker.select-${field.name}`);
    $fieldElement.selectpicker("refresh");

    if (value === "" || (Array.isArray(value) && value.length === 0)) {
      $fieldElement.selectpicker("deselectAll");
    }
  }, [value]);

  // Value in formData is updated
  React.useEffect(() => {
    setValue(formData[field.name] || defaultValue);
  }, [formData[field.name]]);

  return (
    // bootstrap classes:
    //  - form-control
    //  - is-invalid
    //  - selectpicker

    <>
      <select
        className={`
          form-control
          selectpicker
          select-${field.name}
          ${invalidField ? "is-invalid" : ""}
        `}
        id={field.id}
        name={field.name}
        placeholder={field.placeholder}
        style={field.style}
        required={checkFieldRequiredness(field)}
        value={value}
        onChange={(e) => {
          !disabled && onChange(e, field.name);
          setInvalidField(false);
          setErrors([]);
        }}
        onBlur={onBlur}
        onFocus={onFocus}
        onClick={onClick}
        multiple={field.multiple}
        disabled={disabled}
        data-actions-box={field.multiple ? true : null}
        data-live-search={true}
        data-selected-text-format={field.multiple ? "count > 1" : null}
        data-title={inReviewState ? value : null}
        data-width={"100%"}
      >
        {field.options.map((option, index) => {
          return (
            <option key={`option-${field.id}-${index}`} value={option.value}>
              {option.label}
            </option>
          );
        })}
      </select>

      <Errors messages={errors} />
    </>
  );
}

export { SelectField };
