/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { fieldIsRequired } from '../validation';

function TextareaField({
  field, updateFormData, disabled, initialFormData, isInReviewState, isInvalid, validationErrors,
}) {
  const initialValue = initialFormData ? initialFormData[field.name] : "";

  return (<>
    <textarea
      className={`
        form-control
        ${isInvalid ? "is-invalid" : ""}
      `}
      id={field.id}
      name={field.name}
      placeholder={field.placeholder}
      style={field.style}
      required={fieldIsRequired(field)}
      defaultValue={initialValue}
      onChange={(e) => !disabled && updateFormData(e, field.name, e.target.value)}
      disabled={disabled}
    />

    {validationErrors && (
      <div className={`invalid-feedback`}>
        {validationErrors.join("\n")}
      </div>
    )}
  </>);
}

export { TextareaField };
