/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import $ from "jquery";
import "bootstrap"
import "bootstrap-select";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors";

function SelectField({
  field, updateFormData, disabled, initialFormData, inReviewState, invalid, validationErrors,
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
    if (invalid) {
      $(`.bootstrap-select.select-${field.name}`).addClass("is-invalid");
    } else {
      $(`.bootstrap-select.select-${field.name}`).removeClass("is-invalid");
    }
  }, [invalid]);

  React.useEffect(() => {
    $(`.selectpicker.select-${field.name}`).selectpicker();
  }, []);

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
          ${invalid ? "is-invalid" : ""}
        `}
        id={field.id}
        name={field.name}
        placeholder={field.placeholder}
        style={field.style}
        required={checkFieldRequiredness(field)}
        defaultValue={initialValue}
        onChange={(e) => !disabled && onChange(e, field.name)}
        multiple={field.multiple}
        disabled={disabled}
        data-actions-box={field.multiple ? true : null}
        data-live-search={true}
        data-selected-text-format={field.multiple ? "count > 1" : null}
        data-title={inReviewState ? initialValue : null}
        data-width={"100%"}
      >
        {field.options.map(( option, index ) => {
          return (
            <option
              key={`option-${field.id}-${index}`}
              value={option.value}
            >
              {option.label}
            </option>
          );
        })}
      </select>

      <Errors messages={validationErrors} />
    </>
  );
}

export { SelectField };
