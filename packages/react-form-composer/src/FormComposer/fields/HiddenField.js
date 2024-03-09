/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function HiddenField({
  field,
  formData,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  customTriggers,
}) {
  const initialValue = initialFormData ? initialFormData[field.name] : "";

  return (
    // bootstrap classes:
    //  - form-control

    <>
      <input
        className={`
          form-control
        `}
        id={field.id}
        name={field.name}
        type={field.type}
        required={false}
        defaultValue={initialValue}
        onChange={(e) => {
          !disabled && updateFormData(field.name, e.target.value, e);
        }}
      />
    </>
  );
}

export { HiddenField };
