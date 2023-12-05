/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function RadioField({ field, updateFormData }) {
  return (
    field.options.map(( option, index ) => {
      return (
        <div
          key={`option-${field.id}-${index}`}
          className={`form-check`}
        >
          <input
            className={`form-check-input`}
            id={`${field.id}-${index}`}
            name={field.name}
            type={field.type}
            style={field.style}
            required={field.required}
            value={option.value}
            checked={option.checked}
            onChange={(e) => updateFormData(e, field.name)}
          />
          <label className={`form-check-label`} htmlFor={`${field.id}-${index}`}>
            {option.label}
          </label>
        </div>
      );
    })
  );
}

export { RadioField };
