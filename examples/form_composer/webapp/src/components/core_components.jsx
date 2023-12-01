/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="hero is-light" data-cy="directions-container">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}

function FormComposer({ data, onSubmit }) {
   const [form, setForm] = React.useState({});

  let formName = data.name;
  let formInstruction = data.instruction;
  let formSections = data.sections;
  let formSubmitButton = data.submit_button;

  function updateFormData(e, fieldName) {
    setForm((prevState) => {
      return {...prevState, ...{ [fieldName]: e.target.value} }
    });
  }

  React.useEffect(() => {
    if (formSections.length) {
      const initialFormData = {};

      formSections.map((section) => {
        section.fieldsets.map((fieldset) => {
          fieldset.rows.map((row) => {
            row.fields.map((field) => {
              initialFormData[field.name] = field.value;
            });
          });
        });
      });

      setForm(initialFormData);
    }
  }, [formSections]);

  return (
    <form
      className={`form`}
      method={"POST"}
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
    >
      {(formName || formInstruction) && (
        <div className={`alert alert-primary`} role={"alert"}>
          {formName && (
            <h2 className={`form-name`}>{formName}</h2>
          )}

          {formName && formInstruction && <hr />}

          {formInstruction && (
            <p className={`form-instruction`}>{formInstruction}</p>
          )}
        </div>
      )}

      {formSections.map(( section, index ) => {
        let sectionName = section.name;
        let sectionInstruction = section.instruction;
        let fieldsets = section.fieldsets;

        return (
          <section
            key={`section-${index}`}
            className={`section container`}
          >
            {(sectionName || sectionInstruction) && (
              <div className={`alert alert-info`} role={"alert"}>
                {sectionName && (
                  <h4 className={`section-name`}>{sectionName}</h4>
                )}

                {sectionName && sectionInstruction && <hr />}

                {sectionInstruction && (
                  <p className={`section-instruction`}>{sectionInstruction}</p>
                )}
              </div>
            )}

            {fieldsets.map(( fieldset, index ) => {
              let fieldsetName = fieldset.name;
              let fieldsetInstruction = fieldset.instruction;
              let rows = fieldset.rows;

              return (
                <fieldset
                  key={`fieldset-${index}`}
                  className={`fieldset container`}
                >
                  {(fieldsetName || fieldsetInstruction) && (
                    <div className={`fieldset-header alert alert-secondary`} role={"alert"}>
                      {fieldsetName && (
                        <h5 className={`fieldset-name`}>{fieldsetName}</h5>
                      )}

                      {fieldsetName && fieldsetInstruction && <hr />}

                      {fieldsetInstruction && (
                        <p className={`fieldset-instruction`}>{fieldsetInstruction}</p>
                      )}
                    </div>
                  )}

                  {rows.map(( row, index ) => {
                    let rowHelp = row.help;
                    let fields = row.fields;

                    return (
                      <div
                        key={`row-${index}`}
                        className={`row`}
                      >
                        {fields.map(( field, index ) => {
                          let fieldHelp = field.help;

                          return (
                            <div
                              key={`field-${index}`}
                              className={
                                `${field.class ? field.class : ""}
                                field
                                form-group
                                col
                                ${field.required ? "required" : ""}`
                              }
                            >

                              <i>{field.icon}</i>
                              <label htmlFor={field.id}>
                                {field.label}
                              </label>

                              {["input", "email", "password", "number"].includes(field.type) && (
                                <input
                                  className={`form-control`}
                                  id={field.id}
                                  name={field.name}
                                  type={field.type}
                                  placeholder={field.placeholder}
                                  style={field.style}
                                  required={field.required}
                                  onChange={(e) => updateFormData(e, field.name)}
                                />
                              )}

                              {field.type === "select" && (
                                <select
                                  className={`form-control`}
                                  id={field.id}
                                  name={field.name}
                                  placeholder={field.placeholder}
                                  style={field.style}
                                  required={field.required}
                                  onChange={(e) => updateFormData(e, field.name)}
                                >
                                  {field.options.map(( option, index ) => {
                                    return (
                                      <option
                                        key={`option-${field.id}-${index}`}
                                        value={option.value}
                                      >
                                        {option.name}
                                      </option>
                                    );
                                  })}
                                </select>
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
          </section>
        );
      })}

      {formSubmitButton && (<>
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

function AutoComposingFormFrontend({ taskData, onSubmit, onError }) {
  let formData = taskData.form;

  if (!formData) {
    return (
      <div>
        Passed form data is invalid... Recheck your task config.
      </div>
    );
  }

  return (
    <div>
      <FormComposer data={formData} onSubmit={onSubmit} />
    </div>
  );
}

export { LoadingScreen, AutoComposingFormFrontend };
