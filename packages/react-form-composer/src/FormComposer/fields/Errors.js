/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

export function Errors({ messages }) {
  return (
    // bootstrap classes:
    //  - invalid-feedback

    <>
      {messages && messages.length > 0 && (
        <div className={`invalid-feedback`}>
          {messages.map((message, i) => {
            return <div key={`message-${i}`}>{message}</div>;
          })}
        </div>
      )}
    </>
  );
}
