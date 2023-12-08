/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function FileField({ field, updateFormData, disabled, initialFormData }) {
  const initialValue = initialFormData ? initialFormData[field.name] : "";

  return (
    <div className={`custom-file`}>
      <input
        className={`custom-file-input`}
        id={field.id}
        name={field.name}
        type={field.type}
        placeholder={field.placeholder}
        style={field.style}
        required={field.required}
        defaultValue={initialValue}
        onChange={(e) => !disabled && updateFormData(e, field.name, e.target.value)}
        disabled={disabled}
      />
      <label className={`custom-file-label`} htmlFor={field.id}>
        {field.label}
      </label>
    </div>
  );
}

export { FileField };
