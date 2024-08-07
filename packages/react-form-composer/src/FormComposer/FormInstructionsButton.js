/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

export function FormInstructionsButton({ onClick }) {
  return (
    // bootstrap classes:
    //  - btn
    //  - btn-primary
    //  - btn-sm

    <button
      className={`form-instruction-button btn btn-primary btn-sm`}
      data-target={"#id-form-instruction-modal"}
      data-toggle={"modal"}
      onClick={onClick}
      type={"button"}
    >
      <span>&#9432;</span> Task Instructions
    </button>
  );
}
