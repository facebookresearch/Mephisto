/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { CONNECTION_STATUS } from "mephisto-task";

function ConnectionIndicator({ connectionStatus }) {
  let backgroundColor = null;
  let text = "";
  switch (connectionStatus) {
    case CONNECTION_STATUS.CONNECTED:
      backgroundColor = "#5cb85c";
      text = "connected";
      break;
    case CONNECTION_STATUS.RECONNECTING_ROUTER:
      backgroundColor = "#f0ad4e";
      text = "reconnecting to router";
      break;
    case CONNECTION_STATUS.RECONNECTING_SERVER:
      backgroundColor = "#f0ad4e";
      text = "reconnecting to server";
      break;
    case CONNECTION_STATUS.DISCONNECTED_SERVER:
    case CONNECTION_STATUS.DISCONNECTED_ROUTER:
    default:
      backgroundColor = "#d9534f";
      text = "disconnected";
      break;
  }

  return (
    <button
      id="connected-button"
      className="btn btn-lg connection-indicator"
      style={{ backgroundColor: backgroundColor }}
      disabled={true}
    >
      {text}
    </button>
  );
}

export default ConnectionIndicator;
