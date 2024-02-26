/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors";

function FileField({
  field,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  invalid,
  validationErrors,
  onReviewFileButtonClick,
}) {
  const [widgetValue, setWidgetValue] = React.useState("");

  const [invalidField, setInvalidField] = React.useState(false);
  const [errors, setErrors] = React.useState([]);

  // Methods
  function onChange(e, fieldName) {
    let fieldValue = null;
    const input = e.target;

    // Format of JSON value of files that server requires
    input.files?.length &&
      Object.values(input.files).forEach((file) => {
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
    const initialValue = initialFormData
      ? initialFormData[field.name]
      : { name: "" };
    setWidgetValue(initialValue.name || "");
  }

  function onReviewFileClick() {
    onReviewFileButtonClick(widgetValue);
  }

  // Effects
  React.useEffect(() => {
    if (!widgetValue) {
      setDefaultWidgetValue();
    }
  }, []);

  React.useEffect(() => {
    setInvalidField(invalid);
  }, [invalid]);

  React.useEffect(() => {
    setErrors(validationErrors);
  }, [validationErrors]);

  return (
    // bootstrap classes:
    //  - custom-file
    //  - is-invalid
    //  - custom-file-input
    //  - custom-file-label

    <div
      className={`
      file-field
      custom-file
      ${invalidField ? "is-invalid" : ""}
    `}
    >
      <input
        className={`
          custom-file-input
          ${invalidField ? "is-invalid" : ""}
        `}
        id={field.id}
        name={field.name}
        type={field.type}
        placeholder={field.placeholder}
        style={field.style}
        required={checkFieldRequiredness(field)}
        onChange={(e) => {
          !disabled && onChange(e, field.name);
          setInvalidField(false);
          setErrors([]);
        }}
        disabled={disabled}
      />

      {/*
        Button to open file in modal window in Review App.
        This button is shown over input browse button only in review state and if file was attached
      */}
      {inReviewState && widgetValue && (
        <div
          className={"review-file-button"}
          title={"View uploaded file content"}
          onClick={onReviewFileClick}
        >
          View file
        </div>
      )}

      <span className={`custom-file-label`}>{widgetValue}</span>

      <Errors messages={errors} />
    </div>
  );
}

export { FileField };
