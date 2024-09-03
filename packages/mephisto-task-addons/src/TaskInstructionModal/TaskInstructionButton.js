/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import "./TaskInstructionButton.css";

export default function TaskInstructionButton({ onClick }) {
  return (
    // bootstrap classes:
    //  - btn
    //  - btn-primary
    //  - btn-sm

    <button
      className={`task-instruction-button btn btn-primary btn-sm`}
      data-target={"#id-task-instruction-modal"}
      data-toggle={"modal"}
      onClick={onClick}
      type={"button"}
    >
      <span>&#9432;</span> Task Instructions
    </button>
  );
}
