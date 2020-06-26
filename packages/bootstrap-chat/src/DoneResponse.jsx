import React from "react";
import DoneButton from "./DoneButton.jsx";

function DoneResponse({ onMessageSend, isTaskDone, doneText }) {
  // TODO maybe move to CSS?
  let pane_style = {
    paddingLeft: "25px",
    paddingTop: "20px",
    paddingBottom: "20px",
    paddingRight: "25px",
    float: "left",
  };
  return (
    <div
      id="response-type-done"
      className="response-type-module"
      style={pane_style}
    >
      {doneText ? (
        <span id="inactive" style={{ fontSize: "14pt", marginRight: "15px" }}>
          {doneText}
        </span>
      ) : null}
      {isTaskDone ? <DoneButton onMessageSend={onMessageSend} /> : null}
    </div>
  );
}

export default DoneResponse;
