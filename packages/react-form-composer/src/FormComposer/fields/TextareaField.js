/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors";

function TextareaField({
  field,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  invalid,
  validationErrors,
}) {
  const initialValue = initialFormData ? initialFormData[field.name] : "";

  const [invalidField, setInvalidField] = React.useState(false);
  const [errors, setErrors] = React.useState([]);

  // Effects
  React.useEffect(() => {
    setInvalidField(invalid);
  }, [invalid]);

  React.useEffect(() => {
    setErrors(validationErrors);
  }, [validationErrors]);

  return (
    // bootstrap classes:
    //  - form-control
    //  - is-invalid

    <>
      <textarea
        className={`
          form-control
          ${invalidField ? "is-invalid" : ""}
        `}
        id={field.id}
        name={field.name}
        placeholder={field.placeholder}
        style={field.style}
        required={checkFieldRequiredness(field)}
        defaultValue={initialValue}
        onChange={(e) => {
          !disabled && updateFormData(e, field.name, e.target.value);
          setInvalidField(false);
          setErrors([]);
        }}
        disabled={disabled}
      />

      <Errors messages={errors} />
    </>
  );
}

export { TextareaField };
