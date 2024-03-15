/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

const DEFAULT_VALUE = "";

function HiddenField({
  field,
  formData,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  formFields,
  customTriggers,
}) {
  const [value, setValue] = React.useState(DEFAULT_VALUE);

  // --- Effects ---
  // Value in formData is updated
  React.useEffect(() => {
    setValue(formData[field.name] || DEFAULT_VALUE);
  }, [formData[field.name]]);

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
        value={value}
        onChange={(e) => {
          !disabled && updateFormData(field.name, e.target.value, e);
        }}
      />
    </>
  );
}

export { HiddenField };
