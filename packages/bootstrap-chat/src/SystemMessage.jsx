/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
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
