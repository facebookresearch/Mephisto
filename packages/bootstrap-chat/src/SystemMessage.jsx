/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import Glyphicon from "./Glyphicon.jsx";

function SystemMessage({ glyphicon, text }) {
  return (
    <div
      id="waiting-for-message"
      className="row"
      style={{ marginLeft: "0", marginRight: "0" }}
    >
      <div
        className="alert alert-warning message"
        role="alert"
        style={{
          backgroundColor: "#fff",
        }}
      >
        {glyphicon ? <Glyphicon name={glyphicon} /> : null}
        <span style={{ fontSize: "16px" }}>{text}</span>
      </div>
    </div>
  );
}

export default SystemMessage;
