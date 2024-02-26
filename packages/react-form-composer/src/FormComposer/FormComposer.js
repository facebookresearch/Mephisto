/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  DEFAULT_COLLAPSABLE,
  DEFAULT_INITIALLY_COLLAPSED,
  MESSAGES_IN_REVIEW_FILE_DATA_KEY,
} from "./constants";
import { CheckboxField } from "./fields/CheckboxField";
import { FileField } from "./fields/FileField";
import { InputField } from "./fields/InputField";
import { RadioField } from "./fields/RadioField";
import { SelectField } from "./fields/SelectField";
import { TextareaField } from "./fields/TextareaField";
import "./FormComposer.css";
import { FormErrors } from "./FormErrors";
import { SectionErrors } from "./SectionErrors";
import { SectionErrorsCountBadge } from "./SectionErrorsCountBadge";
import { formatStringWithProcedureTokens, setPageTitle } from "./utils";
import {
  checkFieldRequiredness,
  validateFormFields,
} from "./validation/helpers";

function FormComposer({
  data,
  onSubmit,
  finalResults,
  serverSubmitErrors,
  setRenderingErrors,
}) {
  // State to hide submit button
  const [onSubmitLoading, setOnSubmitLoading] = React.useState(false);

  // List of unexpected server error messages
  const [submitErrors, setSubmitErrors] = React.useState([]);

  // Invalid fields (having error messages after form validation)
  const [invalidFormFields, setInvalidFormFields] = React.useState({});

  // Form data for submission
  const [form, setForm] = React.useState({});

  // All fields lookup by their name: { <fieldName>: <field> }
  const [fields, setFields] = React.useState({});

  // Fild list by section index for error display: { <sectionIndex>: <Array<field>> }
  const [sectionsFields, setSectionsFields] = React.useState({});

  const inReviewState = finalResults !== null;

  const formatStringWithTokens = inReviewState
    ? (v, _) => {
        return v;
      } // Return value as is, ignoring whole formatting
    : formatStringWithProcedureTokens;

  let formTitle = formatStringWithTokens(data.title, setRenderingErrors);
  let formInstruction = formatStringWithTokens(
    data.instruction,
    setRenderingErrors
  );
  let formSections = data.sections;
  let formSubmitButton = data.submit_button;

  function updateFormData(e, fieldName, value) {
    if (e) {
      e.preventDefault();
    }

    setForm((prevState) => {
      return {
        ...prevState,
        ...{ [fieldName]: value },
      };
    });
  }

  function scrollToFirstInvalidSection() {
    const firstInvalidSection = document.querySelectorAll(
      "section[data-invalid='true']"
    )[0];
    if (firstInvalidSection) {
      window.scrollTo(0, firstInvalidSection.offsetTop);
    }
  }

  function validateForm(e) {
    // Clean previously invalidated fields
    setInvalidFormFields({});

    // Set new invalid fields
    const _invalidFormFields = validateFormFields(form, fields);
    setInvalidFormFields(_invalidFormFields);

    return !Object.keys(_invalidFormFields).length;
  }

  function prepareFormData() {
    // Append JSON data
    const formData = new FormData();
    formData.append("final_data", form);
    formData.append("final_string_data", JSON.stringify(form));

    // Append files
    const fileInputs = document.querySelectorAll("input[type='file']");
    fileInputs.forEach((input) => {
      input.files?.length &&
        Object.values(input.files).forEach((file) => {
          formData.append(input.name, file, file.name);
        });
    });

    return formData;
  }

  function onSubmitForm(e) {
    e.preventDefault();
    e.stopPropagation();

    const formIsValid = validateForm(e);

    if (!formIsValid) {
      return;
    }

    const formData = prepareFormData();

    // Pass data to `mephisto-task` library
    setOnSubmitLoading(true);
    onSubmit(formData);
  }

  function sendMessageToReviewAppWithFileInfo(filename) {
    // Send file field information to the Review app as a message from iframe
    window.top.postMessage(
      JSON.stringify({
        [MESSAGES_IN_REVIEW_FILE_DATA_KEY]: {
          filename: filename,
        },
      }),
      "*"
    );
  }

  // Effects
  React.useEffect(() => {
    setPageTitle(formTitle);
  }, [formTitle]);

  React.useEffect(() => {
    if (formSections.length) {
      const _fields = {};
      const initialFormData = {};

      formSections.map((section, sectionIndex) => {
        const _sectionFields = [];

        // Set fields to Form fields and Section fields
        section.fieldsets.map((fieldset) => {
          fieldset.rows.map((row) => {
            row.fields.map((field) => {
              _fields[field.name] = field;
              initialFormData[field.name] = field.value;
              _sectionFields.push(field);
            });
          });
        });

        setSectionsFields((prevState) => {
          return {
            ...prevState,
            ...{ [sectionIndex]: _sectionFields },
          };
        });
      });

      setForm(initialFormData);
      setFields(_fields);
    }
  }, [formSections]);

  React.useEffect(() => {
    if (Object.keys(invalidFormFields).length) {
      scrollToFirstInvalidSection();
    }
  }, [invalidFormFields]);

  React.useEffect(() => {
    if (serverSubmitErrors && serverSubmitErrors.length) {
      setSubmitErrors(serverSubmitErrors);
    }
  }, [serverSubmitErrors]);

  return (
    <form
      className={`form-composer`}
      method={"POST"}
      noValidate={true}
      onSubmit={onSubmitForm}
    >
      {(formTitle || formInstruction) && (
        <div className={`form-header alert alert-primary`} role={"alert"}>
          {formTitle && (
            <h2
              className={`form-name`}
              dangerouslySetInnerHTML={{ __html: formTitle }}
            ></h2>
          )}

          {formTitle && formInstruction && <hr />}

          {formInstruction && (
            <p
              className={`form-instruction`}
              dangerouslySetInnerHTML={{ __html: formInstruction }}
            ></p>
          )}
        </div>
      )}

      {/* Accordion with collapsable sections */}
      <div className={`accordion`} id={`id_accordion`}>
        {/* Sections */}
        {formSections.map((section, sectionIndex) => {
          const sectionTitle = formatStringWithTokens(
            section.title,
            setRenderingErrors
          );
          const sectionInstruction = formatStringWithTokens(
            section.instruction,
            setRenderingErrors
          );
          const fieldsets = section.fieldsets;

          const collapsable = [null, undefined].includes(section.collapsable) // Not specified in config
            ? DEFAULT_COLLAPSABLE
            : section.collapsable;
          const initiallyCollapsed = collapsable
            ? [null, undefined].includes(section.initially_collapsed) // Not specified in config
              ? DEFAULT_INITIALLY_COLLAPSED
              : section.initially_collapsed
            : false;

          const sectionHasInvalidFields = !!(
            sectionsFields[sectionIndex] || []
          ).filter((field) =>
            Object.keys(invalidFormFields).includes(field.name)
          ).length;

          return (
            <section
              key={`section-${sectionIndex}`}
              className={`section`}
              data-id={`section-${sectionIndex}`}
              data-invalid={sectionHasInvalidFields}
            >
              {(sectionTitle || sectionInstruction) && (
                // Section header is clickable for accordion
                <div
                  className={`
                    section-header
                    alert
                    alert-info
                    ${collapsable ? "collapsable" : ""}
                    ${sectionHasInvalidFields ? "has-invalid-fields" : ""}
                  `}
                  role={"alert"}
                  id={`accordion_heading_${sectionIndex}`}
                  data-toggle={collapsable ? "collapse" : null}
                  data-target={
                    collapsable
                      ? `#accordion_collapsable_part_${sectionIndex}`
                      : null
                  }
                  aria-expanded={collapsable ? initiallyCollapsed : null}
                  aria-controls={
                    collapsable
                      ? `accordion_collapsable_part_${sectionIndex}`
                      : null
                  }
                >
                  <div className="row justify-content-between">
                    {/* Section name on the left side */}
                    {sectionTitle && (
                      <h4
                        className={`
                          col-8
                          section-name
                          ${collapsable ? "dropdown-toggle" : ""}
                        `}
                        dangerouslySetInnerHTML={{ __html: sectionTitle }}
                      ></h4>
                    )}

                    {/* Badge with errors number on the right side */}
                    <div className={`col-1`}>
                      <SectionErrorsCountBadge
                        sectionFields={sectionsFields[sectionIndex]}
                        invalidFormFields={invalidFormFields}
                      />
                    </div>
                  </div>

                  {sectionTitle && sectionInstruction && <hr />}

                  {sectionInstruction && (
                    <p
                      className={`section-instruction`}
                      dangerouslySetInnerHTML={{ __html: sectionInstruction }}
                    ></p>
                  )}
                </div>
              )}

              {/* Collapsable part of section with fieldsets */}
              <div
                id={`accordion_collapsable_part_${sectionIndex}`}
                className={`
                  collapse
                  ${collapsable ? "" : "non-collapsable"}
                  ${initiallyCollapsed ? "" : "show"}
                `}
                aria-labelledby={`accordion_heading_${sectionIndex}`}
                data-parent={`#id_accordion`}
              >
                <SectionErrors
                  sectionFields={sectionsFields[sectionIndex]}
                  invalidFormFields={invalidFormFields}
                />

                {fieldsets.map((fieldset, fieldsetIndex) => {
                  const fieldsetTitle = formatStringWithTokens(
                    fieldset.title,
                    setRenderingErrors
                  );
                  const fieldsetInstruction = formatStringWithTokens(
                    fieldset.instruction,
                    setRenderingErrors
                  );
                  const rows = fieldset.rows;

                  return (
                    <fieldset
                      key={`fieldset-${fieldsetIndex}`}
                      className={`fieldset container`}
                    >
                      {(fieldsetTitle || fieldsetInstruction) && (
                        <div
                          className={`fieldset-header alert alert-secondary`}
                          role={"alert"}
                        >
                          {fieldsetTitle && (
                            <h5
                              className={`fieldset-name`}
                              dangerouslySetInnerHTML={{
                                __html: fieldsetTitle,
                              }}
                            ></h5>
                          )}

                          {fieldsetTitle && fieldsetInstruction && <hr />}

                          {fieldsetInstruction && (
                            <p
                              className={`fieldset-instruction`}
                              dangerouslySetInnerHTML={{
                                __html: fieldsetInstruction,
                              }}
                            ></p>
                          )}
                        </div>
                      )}

                      {rows.map((row, rowIndex) => {
                        const rowHelp = formatStringWithTokens(
                          row.help,
                          setRenderingErrors
                        );
                        const fields = row.fields;

                        return (
                          <div key={`row-${rowIndex}`} className={`row`}>
                            {fields.map((field, fieldIndex) => {
                              const fieldLabel = formatStringWithTokens(
                                field.label,
                                setRenderingErrors
                              );
                              const fieldTooltip = formatStringWithTokens(
                                field.tooltip,
                                setRenderingErrors
                              );
                              const fieldHelp = field.help;

                              return (
                                <div
                                  key={`field-${fieldIndex}`}
                                  className={`
                                    ${field.class ? field.class : ""}
                                    field
                                    form-group
                                    col
                                    ${
                                      checkFieldRequiredness(field)
                                        ? "required"
                                        : ""
                                    }
                                  `}
                                  title={fieldTooltip}
                                >
                                  <i>{field.icon}</i>
                                  <label htmlFor={field.id}>{fieldLabel}</label>

                                  {[
                                    "input",
                                    "email",
                                    "password",
                                    "number",
                                  ].includes(field.type) && (
                                    <InputField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={
                                        (invalidFormFields[field.name] || [])
                                          .length
                                      }
                                      validationErrors={
                                        invalidFormFields[field.name] || []
                                      }
                                    />
                                  )}

                                  {field.type === "textarea" && (
                                    <TextareaField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={
                                        (invalidFormFields[field.name] || [])
                                          .length
                                      }
                                      validationErrors={
                                        invalidFormFields[field.name] || []
                                      }
                                    />
                                  )}

                                  {field.type === "checkbox" && (
                                    <CheckboxField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={
                                        (invalidFormFields[field.name] || [])
                                          .length
                                      }
                                      validationErrors={
                                        invalidFormFields[field.name] || []
                                      }
                                    />
                                  )}

                                  {field.type === "radio" && (
                                    <RadioField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={
                                        (invalidFormFields[field.name] || [])
                                          .length
                                      }
                                      validationErrors={
                                        invalidFormFields[field.name] || []
                                      }
                                    />
                                  )}

                                  {field.type === "select" && (
                                    <SelectField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={
                                        (invalidFormFields[field.name] || [])
                                          .length
                                      }
                                      validationErrors={
                                        invalidFormFields[field.name] || []
                                      }
                                    />
                                  )}

                                  {field.type === "file" && (
                                    <FileField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={
                                        (invalidFormFields[field.name] || [])
                                          .length
                                      }
                                      validationErrors={
                                        invalidFormFields[field.name] || []
                                      }
                                      onReviewFileButtonClick={
                                        sendMessageToReviewAppWithFileInfo
                                      }
                                    />
                                  )}

                                  {fieldHelp && (
                                    <small
                                      className={`field-help form-text text-muted`}
                                      dangerouslySetInnerHTML={{
                                        __html: fieldHelp,
                                      }}
                                    ></small>
                                  )}
                                </div>
                              );
                            })}

                            {rowHelp && (
                              <div
                                className={`row-help container`}
                                dangerouslySetInnerHTML={{ __html: rowHelp }}
                              ></div>
                            )}
                          </div>
                        );
                      })}
                    </fieldset>
                  );
                })}
              </div>
            </section>
          );
        })}
      </div>

      {/* Submit button */}
      {formSubmitButton && !inReviewState && (
        <>
          <hr className={`form-buttons-separator`} />

          {onSubmitLoading ? (
            // Banner of success
            <div
              className={`alert alert-success centered mx-auto col-6 ml-2 mr-2`}
            >
              Thank you!
              <br />
              Your form has been submitted.
            </div>
          ) : (
            <>
              {/* Button instruction */}
              {formSubmitButton.instruction && (
                <div
                  className={`alert alert-light centered mx-auto col-6 ml-2 mr-2`}
                  dangerouslySetInnerHTML={{
                    __html: formSubmitButton.instruction,
                  }}
                ></div>
              )}

              {/* Submit button */}
              <div className={`form-buttons container`}>
                <button
                  className={`button-submit btn btn-success`}
                  type={"submit"}
                  title={formSubmitButton.tooltip}
                >
                  {formSubmitButton.text}
                </button>
              </div>
            </>
          )}

          {/* Additional reminder to correct form errors above */}
          {!!Object.keys(invalidFormFields).length && (
            <div
              className={`alert alert-danger centered mx-auto col-6 ml-2 mr-2`}
            >
              Please correct validation errors in the form
            </div>
          )}
        </>
      )}

      {/* Unexpected server errors */}
      {!!submitErrors.length && <FormErrors errorMessages={submitErrors} />}
    </form>
  );
}

export { FormComposer };
