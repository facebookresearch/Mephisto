/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

export function SectionErrors({ invalidFormFields, sectionFields }) {
  const allInvalidFieldnames = Object.keys(invalidFormFields);
  const sectionInvalidFields = (sectionFields || []).filter((field) =>
    allInvalidFieldnames.includes(field.name)
  );
  const sectionHasErrors = sectionInvalidFields.length > 0;

  return (
    // bootstrap classes:
    //  - alert
    //  - alert-danger
    //  - container

    <>
      {sectionHasErrors && sectionFields && (
        <div className={`alert alert-danger container`} role={"alert"}>
          <b>Please fix the following errors:</b>

          <ul key={`fields-errors`}>
            {sectionFields.map((field, fieldIndex) => {
              const fieldErrors = invalidFormFields[field.name] || [];
              const fieldHasErrors = fieldErrors.length > 0;

              if (!fieldHasErrors) {
                return;
              }

              return (
                <li key={`fields-errors-${fieldIndex}`}>
                  <div>{field.label}:</div>

                  <ul key={`field-errors`}>
                    {fieldErrors.map((error, errorIndex) => {
                      return (
                        <li key={`field-errors-${fieldIndex}-${errorIndex}`}>
                          {error}
                        </li>
                      );
                    })}
                  </ul>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </>
  );
}
