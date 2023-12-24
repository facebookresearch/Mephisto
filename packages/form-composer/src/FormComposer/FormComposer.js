/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import $ from "jquery";
import React from "react";
import { CheckboxField } from "./fields/CheckboxField";
import { FileField } from "./fields/FileField";
import { InputField } from "./fields/InputField";
import { RadioField } from "./fields/RadioField";
import { SelectField } from "./fields/SelectField";
import { TextareaField } from "./fields/TextareaField";
import "./FormComposer.css";
import { SectionErrors } from "./SectionErrors";
import { SectionErrorsCountBadge } from "./SectionErrorsCountBadge";
import { checkFieldRequiredness, validateFormFields } from "./validation/helpers";

function FormComposer({ data, onSubmit, finalResults }) {
  // Invalid fields (having error messages after form validation)
  const [invalidFormFields, setInvalidFormFields] = React.useState({});

  // Form data for submission
  const [form, setForm] = React.useState({});

  // All fields lookup by their name: { <fieldName>: <field> }
  const [fields, setFields] = React.useState({});

  // Fild list by section index for error display: { <sectionIndex>: <Array<field>> }
  const [sectionsFields, setSectionsFields] = React.useState({});

  const inReviewState = finalResults !== null;

  let formName = data.name;
  let formInstruction = data.instruction;
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

  function validateForm(e) {
    // Clean previously invalidated fields
    setInvalidFormFields({});

    const formElement = e.currentTarget;
    const formFieldElements = $.unique(Object.values(formElement.elements));

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
      input.files?.length && Object.values(input.files).forEach((file) => {
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
    onSubmit(formData);
  }

  // Effects
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

  return (
    <form
      className={`form-composer`}
      method={"POST"}
      noValidate={true}
      onSubmit={onSubmitForm}
    >
      {(formName || formInstruction) && (
        <div className={`alert alert-primary`} role={"alert"}>
          {formName && (
            <h2 className={`form-name`}>
              {formName}
            </h2>
          )}

          {formName && formInstruction && <hr />}

          {formInstruction && (
            <p className={`form-instruction`}>
              {formInstruction}
            </p>
          )}
        </div>
      )}

      {/* Accordion with collapsable sections */}
      <div className={`accordion`} id={`id_accordion`}>

        {/* Sections */}
        {formSections.map(( section, sectionIndex ) => {
          let sectionName = section.name;
          let sectionInstruction = section.instruction;
          let fieldsets = section.fieldsets;

          return (
            <section
              key={`section-${sectionIndex}`}
              className={`section container`}
            >
              {(sectionName || sectionInstruction) && (
                // Section header is clickable for accordion
                <div
                  className={`section-header alert alert-info`}
                  role={"alert"}
                  id={`accordion_heading_${sectionIndex}`}
                  data-toggle={"collapse"}
                  data-target={`#accordion_collapsable_part_${sectionIndex}`}
                  aria-expanded={true}
                  aria-controls={`accordion_collapsable_part_${sectionIndex}`}
                >
                  <div className="row justify-content-between">
                    {/* Section name on the left side */}
                    {sectionName && (
                      <h4 className={`col-8 section-name dropdown-toggle`}>
                        {sectionName}
                      </h4>
                    )}

                    {/* Badge with errors number on the right side */}
                    <div className={`col-1`}>
                      <SectionErrorsCountBadge
                        sectionFields={sectionsFields[sectionIndex]}
                        invalidFormFields={invalidFormFields}
                      />
                    </div>
                  </div>

                  {sectionName && sectionInstruction && <hr />}

                  {sectionInstruction && (
                    <p className={`section-instruction`}>
                      {sectionInstruction}
                    </p>
                  )}
                </div>
              )}

              {/* Collapsable part of section with fieldsets */}
              <div
                id={`accordion_collapsable_part_${sectionIndex}`}
                className={`collapse ${sectionIndex === 0 ? "show" : ""}`}
                aria-labelledby={`accordion_heading_${sectionIndex}`}
                data-parent={`#id_accordion`}
              >
                <SectionErrors
                  sectionFields={sectionsFields[sectionIndex]}
                  invalidFormFields={invalidFormFields}
                />

                {fieldsets.map(( fieldset, fieldsetIndex ) => {
                  let fieldsetName = fieldset.name;
                  let fieldsetInstruction = fieldset.instruction;
                  let rows = fieldset.rows;

                  return (
                    <fieldset
                      key={`fieldset-${fieldsetIndex}`}
                      className={`fieldset container`}
                    >
                      {(fieldsetName || fieldsetInstruction) && (
                        <div className={`fieldset-header alert alert-secondary`} role={"alert"}>
                          {fieldsetName && (
                            <h5 className={`fieldset-name`}>
                              {fieldsetName}
                            </h5>
                          )}

                          {fieldsetName && fieldsetInstruction && <hr />}

                          {fieldsetInstruction && (
                            <p className={`fieldset-instruction`}>
                              {fieldsetInstruction}
                            </p>
                          )}
                        </div>
                      )}

                      {rows.map(( row, rowIndex ) => {
                        let rowHelp = row.help;
                        let fields = row.fields;

                        return (
                          <div
                            key={`row-${rowIndex}`}
                            className={`row`}
                          >
                            {fields.map(( field, fieldIndex ) => {
                              let fieldHelp = field.help;

                              return (
                                <div
                                  key={`field-${fieldIndex}`}
                                  className={
                                    `${field.class ? field.class : ""}
                                    field
                                    form-group
                                    col
                                    ${checkFieldRequiredness(field) ? "required" : ""}`
                                  }
                                >

                                  <i>
                                    {field.icon}
                                  </i>
                                  <label htmlFor={field.id}>
                                    {field.label}
                                  </label>

                                  {["input", "email", "password", "number"].includes(field.type) && (
                                    <InputField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={(invalidFormFields[field.name] || []).length}
                                      validationErrors={(invalidFormFields[field.name] || [])}
                                    />
                                  )}

                                  {field.type === "textarea" && (
                                    <TextareaField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={(invalidFormFields[field.name] || []).length}
                                      validationErrors={(invalidFormFields[field.name] || [])}
                                    />
                                  )}

                                  {field.type === "checkbox" && (
                                    <CheckboxField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={(invalidFormFields[field.name] || []).length}
                                      validationErrors={(invalidFormFields[field.name] || [])}
                                    />
                                  )}

                                  {field.type === "radio" && (
                                    <RadioField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={(invalidFormFields[field.name] || []).length}
                                      validationErrors={(invalidFormFields[field.name] || [])}
                                    />
                                  )}

                                  {field.type === "select" && (
                                    <SelectField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={(invalidFormFields[field.name] || []).length}
                                      validationErrors={(invalidFormFields[field.name] || [])}
                                    />
                                  )}

                                  {field.type === "file" && (
                                    <FileField
                                      field={field}
                                      updateFormData={updateFormData}
                                      disabled={inReviewState}
                                      initialFormData={finalResults}
                                      inReviewState={inReviewState}
                                      invalid={(invalidFormFields[field.name] || []).length}
                                      validationErrors={(invalidFormFields[field.name] || [])}
                                    />
                                  )}

                                  {fieldHelp && (
                                    <small className={`field-help form-text text-muted`}>
                                      {fieldHelp}
                                    </small>
                                  )}
                                </div>
                              );
                            })}

                            {rowHelp && (
                              <div className={`row-help container`}>
                                {rowHelp}
                              </div>
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

      {(formSubmitButton && !inReviewState) && (<>
        <hr className={`form-buttons-separator`} />

        <div className={`form-buttons container`}>
          <button
            className={`button-submit btn btn-success`}
            type={"submit"}
            title={formSubmitButton.title}
          >
            {formSubmitButton.text}
          </button>
        </div>
      </>)}
    </form>
  );
}

export { FormComposer };
