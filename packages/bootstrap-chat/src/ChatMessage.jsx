/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function ChatMessage({ isSelf, duration, agentName, message = "" }) {
  const floatToSide = isSelf ? "right" : "left";
  const alertStyle = isSelf ? "alert-info" : "alert-warning";

  return (
    <div className="row" style={{ marginLeft: "0", marginRight: "0" }}>
      <div
        className={"alert message " + alertStyle}
        role="alert"
        style={{ float: floatToSide }}
      >
        <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
          <b>{agentName}</b>: {message}
        </span>
        <ShowDuration duration={duration} />
      </div>
    </div>
  );
}

function ShowDuration({ duration }) {
  if (!duration) return null;

  const durationSeconds = Math.floor(duration / 1000) % 60;
  const durationMinutes = Math.floor(duration / 60000);
  const minutesText = durationMinutes > 0 ? `${durationMinutes} min` : "";
  const secondsText = durationSeconds > 0 ? `${durationSeconds} sec` : "";
  return (
    <small>
      <br />
      <i>Duration: </i>
      {minutesText + " " + secondsText}
    </small>
  );
}

export default ChatMessage;
