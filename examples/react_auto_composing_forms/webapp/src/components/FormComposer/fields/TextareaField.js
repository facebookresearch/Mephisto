/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function TextareaField({ field, updateFormData, disabled, initialFormData }) {
  const initialValue = initialFormData ? initialFormData[field.name] : "";

  return (
    <textarea
      className={`form-control`}
      id={field.id}
      name={field.name}
      placeholder={field.placeholder}
      style={field.style}
      required={field.required}
      defaultValue={initialValue}
      onChange={(e) => !disabled && updateFormData(e, field.name, e.target.value)}
      disabled={disabled}
    />
  );
}

export { TextareaField };
