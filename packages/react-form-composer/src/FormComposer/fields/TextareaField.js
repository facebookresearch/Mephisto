/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors";

function TextareaField({
  field, updateFormData, disabled, initialFormData, inReviewState, invalid, validationErrors,
}) {
  const initialValue = initialFormData ? initialFormData[field.name] : "";

  return (
    // bootstrap classes:
    //  - form-control
    //  - is-invalid

    <>
      <textarea
        className={`
          form-control
          ${invalid ? "is-invalid" : ""}
        `}
        id={field.id}
        name={field.name}
        placeholder={field.placeholder}
        style={field.style}
        required={checkFieldRequiredness(field)}
        defaultValue={initialValue}
        onChange={(e) => !disabled && updateFormData(e, field.name, e.target.value)}
        disabled={disabled}
      />

      <Errors messages={validationErrors} />
    </>
  );
}

export { TextareaField };
