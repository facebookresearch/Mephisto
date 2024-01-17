/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors";

function FileField({
  field, updateFormData, disabled, initialFormData, inReviewState, invalid, validationErrors,
}) {
  const [widgetValue, setWidgetValue] = React.useState("");

  function onChange(e, fieldName) {
    let fieldValue = null;
    const input = e.target;

    // Format of JSON value of files that server requires
    input.files?.length && Object.values(input.files).forEach((file) => {
      fieldValue = {
        lastModified: file.lastModified ? file.lastModified : -1,
        name: file.name ? file.name : "",
        size: file.size ? file.size : -1,
        type: file.type ? file.type : "",
      };
      setWidgetValue(fieldValue.name);
    });

    updateFormData(e, fieldName, fieldValue);
  }

  function setDefaultWidgetValue() {
    const initialValue = initialFormData ? initialFormData[field.name] : {name: ""};
    setWidgetValue(initialValue.name || "");
  }

  React.useEffect(() => {
    if (!widgetValue) {
      setDefaultWidgetValue();
    }
  }, []);

  return (
    // bootstrap classes:
    //  - custom-file
    //  - is-invalid
    //  - custom-file-input
    //  - custom-file-label

    <div className={`
      custom-file 
      ${invalid ? "is-invalid" : ""}
    `}>
      <input
        className={`
          custom-file-input 
          ${invalid ? "is-invalid" : ""}
        `}
        id={field.id}
        name={field.name}
        type={field.type}
        placeholder={field.placeholder}
        style={field.style}
        required={checkFieldRequiredness(field)}
        onChange={(e) => !disabled && onChange(e, field.name)}
        disabled={disabled}
      />

      <span className={`custom-file-label`}>
        {widgetValue}
      </span>

      <Errors messages={validationErrors} />
    </div>
  );
}

export { FileField };