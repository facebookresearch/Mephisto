/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  DEFAULT_COLLAPSABLE,
  DEFAULT_INITIALLY_COLLAPSED,
  FieldType,
  MESSAGES_IN_REVIEW_FILE_DATA_KEY,
} from "./constants";
import { CheckboxField } from "./fields/CheckboxField";
import { FileField } from "./fields/FileField";
import { HiddenField } from "./fields/HiddenField";
import { InputField } from "./fields/InputField";
import { RadioField } from "./fields/RadioField";
import { SelectField } from "./fields/SelectField";
import { TextareaField } from "./fields/TextareaField";
import "./FormComposer.css";
import { FormErrors } from "./FormErrors";
import { FormInstructionsButton } from "./FormInstructionsButton";
import { FormInstructionsModal } from "./FormInstructionsModal";
import { SectionErrors } from "./SectionErrors";
import { SectionErrorsCountBadge } from "./SectionErrorsCountBadge";
import {
  formatStringWithProcedureTokens,
  getDefaultFormFieldValue,
  runCustomTrigger,
  setPageTitle,
} from "./utils";
import {
  checkFieldRequiredness,
  prepareFormDataForSubmit,
  validateFormFields,
} from "./validation/helpers";

function FormComposer({
  data,
  onSubmit,
  finalResults,
  serverSubmitErrors,
  setRenderingErrors,
  customValidators,
  customTriggers,
}) {
  const formComposerConfig = data;

  // State to hide submit button
  const [onSubmitLoading, setOnSubmitLoading] = React.useState(false);

  // List of unexpected server error messages
  const [submitErrors, setSubmitErrors] = React.useState([]);

  // Invalid fields (having error messages after form validation)
  const [invalidFormFields, setInvalidFormFields] = React.useState({});

  // Form data for submission
  const [formState, setFormState] = React.useState({});

  // All fields lookup by their name: { <fieldName>: <field> }
  const [formFields, setFormFields] = React.useState({});

  // Fild list by section index for error display: { <sectionIndex>: <Array<field>> }
  const [sectionsFields, setSectionsFields] = React.useState({});

  // Form instruction modal state
  const [
    formInstrupctionModalOpen,
    setFormInstrupctionModalOpen,
  ] = React.useState(false);

  const inReviewState = finalResults !== null;

  const formatStringWithTokens = inReviewState
    ? (v, _) => {
        return v;
      } // Return value as is, ignoring whole formatting
    : formatStringWithProcedureTokens;

  let formTitle = formatStringWithTokens(
    formComposerConfig.title,
    setRenderingErrors
  );
  let formInstruction = formatStringWithTokens(
    formComposerConfig.instruction,
    setRenderingErrors
  );
  let showFormInstructionAsModal =
    formComposerConfig.show_instructions_as_modal || false;
  let formSections = formComposerConfig.sections;
  let formSubmitButton = formComposerConfig.submit_button;

  function updateFormData(fieldName, value, e) {
    if (e) {
      e.preventDefault();
    }

    setFormState((prevState) => {
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
    const _invalidFormFields = validateFormFields(
      formState,
      formFields,
      customValidators
    );
    setInvalidFormFields(_invalidFormFields);

    return !Object.keys(_invalidFormFields).length;
  }

  function onSubmitForm(e) {
    e.preventDefault();
    e.stopPropagation();

    const formIsValid = validateForm(e);

    if (!formIsValid) {
      return;
    }

    const formData = prepareFormDataForSubmit(formState, formFields);

    // Pass data to `mephisto-task` library
    setOnSubmitLoading(true);
    onSubmit(formData);
  }

  function sendMessageToReviewAppWithFileInfo(filename, fieldname) {
    // Send file field information to the Review app as a message from iframe
    window.top.postMessage(
      JSON.stringify({
        [MESSAGES_IN_REVIEW_FILE_DATA_KEY]: {
          fieldname: fieldname,
          filename: filename,
        },
      }),
      "*"
    );
  }

  function onClickSubmitButton() {
    if (inReviewState) {
      return;
    }

    runCustomTrigger(
      formSubmitButton.triggers,
      "onClick",
      customTriggers,
      formState,
      updateFormData,
      formSubmitButton
    );
  }

  // --- Effects ---
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
              initialFormData[field.name] = getDefaultFormFieldValue(
                field,
                finalResults
              );
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

      setFormState(initialFormData);
      setFormFields(_fields);
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
      className={`form-composer ${formComposerConfig.classes || ""}`}
      id={formComposerConfig.id}
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

          {/* Show instruction or button that opens a modal with instructions */}
          {showFormInstructionAsModal ? (
            <>
              {/* Instructions */}
              {formTitle && formInstruction && <hr />}

              {formInstruction && (
                <div>
                  For instructions, click "Task Instruction" button in the
                  top-right corner.
                </div>
              )}

              {/* Button (modal in the end of the component) */}
              <FormInstructionsButton
                onClick={() =>
                  setFormInstrupctionModalOpen(!formInstrupctionModalOpen)
                }
              />
            </>
          ) : (
            <>
              {/* Instructions */}
              {formTitle && formInstruction && <hr />}

              {formInstruction && (
                <p
                  className={`form-instruction`}
                  dangerouslySetInnerHTML={{ __html: formInstruction }}
                ></p>
              )}
            </>
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

          function onClickSectionHeader() {
            if (inReviewState) {
              return;
            }

            runCustomTrigger(
              section.triggers,
              "onClick",
              customTriggers,
              formState,
              updateFormData,
              data
            );
          }

          return (
            <section
              key={`section-${sectionIndex}`}
              className={`section ${section.classes || ""}`}
              id={section.id}
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
                  onClick={onClickSectionHeader}
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
                      className={`fieldset container ${fieldset.classes || ""}`}
                      id={fieldset.id}
                    >
                      {fieldsetTitle || fieldsetInstruction ? (
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
                      ) : (
                        <hr />
                      )}

                      {rows.map((row, rowIndex) => {
                        const rowHelp = formatStringWithTokens(
                          row.help,
                          setRenderingErrors
                        );
                        const fields = row.fields;

                        return (
                          <div
                            key={`row-${rowIndex}`}
                            className={`row ${row.classes || ""}`}
                            id={row.id}
                          >
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
                                    field
                                    form-group
                                    col
                                    ${
                                      checkFieldRequiredness(field)
                                        ? "required"
                                        : ""
                                    }
                                    ${
                                      field.type === FieldType.HIDDEN
                                        ? "hidden-type"
                                        : ""
                                    }
                                    ${field.classes || ""}
                                  `}
                                  title={fieldTooltip}
                                >
                                  <i>{field.icon}</i>
                                  <label htmlFor={field.id}>{fieldLabel}</label>

                                  {[
                                    FieldType.INPUT,
                                    FieldType.EMAIL,
                                    FieldType.PASSWORD,
                                    FieldType.NUMBER,
                                  ].includes(field.type) && (
                                    <InputField
                                      field={field}
                                      formData={formState}
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
                                      formFields={formFields}
                                      customTriggers={customTriggers}
                                    />
                                  )}

                                  {field.type === FieldType.TEXTAREA && (
                                    <TextareaField
                                      field={field}
                                      formData={formState}
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
                                      formFields={formFields}
                                      customTriggers={customTriggers}
                                    />
                                  )}

                                  {field.type === FieldType.CHECKBOX && (
                                    <CheckboxField
                                      field={field}
                                      formData={formState}
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
                                      formFields={formFields}
                                      customTriggers={customTriggers}
                                    />
                                  )}

                                  {field.type === FieldType.RADIO && (
                                    <RadioField
                                      field={field}
                                      formData={formState}
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
                                      formFields={formFields}
                                      customTriggers={customTriggers}
                                    />
                                  )}

                                  {field.type === FieldType.SELECT && (
                                    <SelectField
                                      field={field}
                                      formData={formState}
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
                                      formFields={formFields}
                                      customTriggers={customTriggers}
                                    />
                                  )}

                                  {field.type === FieldType.FILE && (
                                    <FileField
                                      field={field}
                                      formData={formState}
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
                                      formFields={formFields}
                                      customTriggers={customTriggers}
                                    />
                                  )}

                                  {field.type === FieldType.HIDDEN && (
                                    <HiddenField
                                      field={field}
                                      formData={formState}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      formFields={formFields}
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
        <div
          className={`${formSubmitButton.classes || ""}`}
          id={formSubmitButton.id}
        >
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
                  onClick={onClickSubmitButton}
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
        </div>
      )}

      {/* Unexpected server errors */}
      {!!submitErrors.length && <FormErrors errorMessages={submitErrors} />}

      {/* Modal with form instructions */}
      {showFormInstructionAsModal && formInstruction && (
        <FormInstructionsModal
          instructions={
            <p
              className={`form-instruction`}
              dangerouslySetInnerHTML={{ __html: formInstruction }}
            ></p>
          }
          open={formInstrupctionModalOpen}
          setOpen={setFormInstrupctionModalOpen}
          title={"Task Instructions"}
        />
      )}
    </form>
  );
}

export { FormComposer };
