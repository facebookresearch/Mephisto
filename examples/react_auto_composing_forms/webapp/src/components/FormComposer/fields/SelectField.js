/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import $ from "jquery";
import "bootstrap"
import "bootstrap-select";
import { fieldIsRequired } from '../validation';

function SelectField({
  field, updateFormData, disabled, initialFormData, isInReviewState, isInvalid, validationErrors,
}) {
  const initialValue = (
    initialFormData
      ? initialFormData[field.name]
      : (field.multiple ? [] : "")
  );

  function onChange(e, fieldName) {
    let fieldValue = e.target.value;
    if (field.multiple) {
      fieldValue = Array.from(e.target.selectedOptions, option => option.value);
    }

    updateFormData(e, fieldName, fieldValue);
  }

  React.useEffect(() => {
    if (isInvalid) {
      $(`.bootstrap-select.select-${field.name}`).addClass("is-invalid");
    } else {
      $(`.bootstrap-select.select-${field.name}`).removeClass("is-invalid");
    }
  }, [isInvalid]);

  React.useEffect(() => {
    $(`.selectpicker.select-${field.name}`).selectpicker();
  }, []);

  return (<>
    <select
      className={`
        form-control 
        selectpicker
        select-${field.name}
        ${isInvalid ? "is-invalid" : ""}
      `}
      id={field.id}
      name={field.name}
      placeholder={field.placeholder}
      style={field.style}
      required={fieldIsRequired(field)}
      defaultValue={initialValue}
      onChange={(e) => !disabled && onChange(e, field.name)}
      multiple={field.multiple}
      disabled={disabled}
      data-actions-box={field.multiple ? true : null}
      data-live-search={true}
      data-selected-text-format={field.multiple ? "count > 1" : null}
      data-title={isInReviewState ? initialValue : null}
      data-width={"100%"}
    >
      {field.options.map(( option, index ) => {
        return (
          <option
            key={`option-${field.id}-${index}`}
            value={option.value}
          >
            {option.name}
          </option>
        );
      })}
    </select>

    {validationErrors && (
      <div className={`invalid-feedback`}>
        {validationErrors.join("\n")}
      </div>
    )}
  </>);
}

export { SelectField };
