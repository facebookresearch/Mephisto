/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

export function FormErrors({ errorMessages }) {
  return (
    // bootstrap classes:
    //  - alert
    //  - alert-danger
    //  - ml-2
    //  - mr-2
    //  - mx-auto
    //  - col-6

    <>
      <div
        className={`alert alert-danger mx-auto col-6 ml-2 mr-2`}
        role={"alert"}
      >
        <b>Could not submit the form:</b>

        <ul>
          {errorMessages.map((message, index) => {
            return <li key={`error-message-${index}`}>{message}</li>;
          })}
        </ul>
      </div>
    </>
  );
}
