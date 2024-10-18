/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  AUDIO_TYPES_BY_EXT,
  FILE_TYPE_BY_EXT,
  FileType,
  VIDEO_TYPES_BY_EXT,
} from "../constants";
import { runCustomTrigger } from "../utils";
import { checkFieldRequiredness } from "../validation/helpers";
import { Errors } from "./Errors.jsx";
import "./FileField.css";

const DEFAULT_VALUE = "";

function FileField({
  field,
  formData,
  updateFormData,
  disabled,
  initialFormData,
  inReviewState,
  invalid,
  validationErrors,
  formFields,
  customTriggers,
  cleanErrorsOnChange,
  onReviewFileButtonClick,
}) {
  const [value, setValue] = React.useState(DEFAULT_VALUE);

  const [invalidField, setInvalidField] = React.useState(false);
  const [errors, setErrors] = React.useState([]);

  const [fileUrl, setFileUrl] = React.useState(null);
  const [fileExt, setFileExt] = React.useState(null);

  const fileType = FILE_TYPE_BY_EXT[fileExt];

  // Methods
  function _runCustomTrigger(triggerName) {
    if (inReviewState) {
      return;
    }

    runCustomTrigger(
      field.triggers,
      triggerName,
      customTriggers,
      formData,
      updateFormData,
      field,
      value,
      formFields
    );
  }

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
          file: file,
        };
        setFileExt(fieldValue.name.split(".").pop().toLowerCase());
        setFileUrl(URL.createObjectURL(file));
      });

    updateFormData(fieldName, fieldValue, e);
    _runCustomTrigger("onChange");
  }

  function onBlur(e) {
    _runCustomTrigger("onBlur");
  }

  function onFocus(e) {
    _runCustomTrigger("onFocus");
  }

  function onClick(e) {
    _runCustomTrigger("onClick");
  }

  function setDefaultWidgetValue() {
    const initialValue = initialFormData
      ? initialFormData[field.name]
      : { name: DEFAULT_VALUE };
    updateFormData(field.name, initialValue);
  }

  function onReviewFileClick() {
    onReviewFileButtonClick(value, field.name);
  }

  // --- Effects ---
  React.useEffect(() => {
    setDefaultWidgetValue();
  }, []);

  React.useEffect(() => {
    setInvalidField(invalid);
  }, [invalid]);

  React.useEffect(() => {
    setErrors(validationErrors);
  }, [validationErrors]);

  // Value in formData is updated
  React.useEffect(() => {
    const fieldValue = formData[field.name];
    const fileName = fieldValue ? fieldValue.name : DEFAULT_VALUE;
    setValue(fileName);
  }, [formData[field.name]]);

  return (
    // bootstrap classes:
    //  - custom-file
    //  - is-invalid
    //  - custom-file-input
    //  - custom-file-label

    <div
      className={`
      fc-file-field
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
          if (cleanErrorsOnChange) {
            setInvalidField(false);
            setErrors([]);
          }
        }}
        onBlur={onBlur}
        onFocus={onFocus}
        onClick={onClick}
        disabled={disabled}
      />

      {/*
        Button to open file in modal window in Review App.
        This button is shown over input browse button only in review state and if file was attached
      */}
      {inReviewState && value && (
        <div
          className={"review-file-button"}
          title={"View uploaded file content"}
          onClick={onReviewFileClick}
        >
          View file
        </div>
      )}

      <span className={`custom-file-label`}>{value}</span>

      <Errors messages={errors} />

      {field.show_preview && fileType && (
        <div className={"file-preview"}>
          {fileType === FileType.IMAGE && (
            <img
              id={`${field.id}_preview`}
              src={fileUrl}
              alt={`image "${value}"`}
            />
          )}
          {fileType === FileType.VIDEO && (
            <video id={`${field.id}_preview`} controls={true}>
              <source src={fileUrl} type={VIDEO_TYPES_BY_EXT[fileExt]} />
            </video>
          )}
          {fileType === FileType.AUDIO && (
            <div className={"audio-wrapper"}>
              <audio id={`${field.id}_preview`} controls={true}>
                <source src={fileUrl} type={AUDIO_TYPES_BY_EXT[fileExt]} />
              </audio>
            </div>
          )}
          {fileType === FileType.PDF && (
            <div className={"pdf-wrapper"}>
              <iframe
                id={`${field.id}_preview`}
                src={`${fileUrl}#view=fit&page=1&toolbar=0&navpanes=0`}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export { FileField };
