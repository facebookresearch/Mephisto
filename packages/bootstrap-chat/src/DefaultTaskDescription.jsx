/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

function DefaultTaskDescription({ chatTitle, taskDescriptionHtml, children }) {
  return (
    <div>
      <h1>{chatTitle}</h1>
      <hr style={{ borderTop: "1px solid #555" }} />
      {children}
      {children ? <hr style={{ borderTop: "1px solid #555" }} /> : null}
      <span
        id="task-description"
        style={{ fontSize: "16px" }}
        dangerouslySetInnerHTML={{
          __html: taskDescriptionHtml || "Task Description Loading",
        }}
      />
    </div>
  );
}

export default DefaultTaskDescription;
