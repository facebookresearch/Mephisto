/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import $ from "jquery";
import "bootstrap"
import "bootstrap-select";

function SelectField({ field, updateFormData, disabled, initialFormData }) {
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
    $('.selectpicker').selectpicker();
  }, []);

  return (
    <select
      className={`form-control custom-select selectpicker`}
      id={field.id}
      name={field.name}
      placeholder={field.placeholder}
      style={field.style}
      required={field.required}
      defaultValue={initialValue}
      onChange={(e) => !disabled && onChange(e, field.name)}
      multiple={field.multiple}
      disabled={disabled}
      data-live-search={true}
      data-selected-text-format={field.multiple ? "count > 1" : null}
      data-width={"auto"}
      data-actions-box={field.multiple ? true : null}
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
  );
}

export { SelectField };
