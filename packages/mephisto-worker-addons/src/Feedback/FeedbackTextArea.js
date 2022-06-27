import React from "react";
import { handleChangeFeedback } from "../Functions";
import "./index.css";

function FeedbackTextArea({
  setTriggerRef,
  widths,
  feedbackText,
  setFeedbackText,
  stylePrefix,
  state,
  dispatch,
  maxFeedbackLength,
  id,
}) {
  return (
    <textarea
      id={id}
      ref={setTriggerRef}
      style={{
        minWidth: widths.min,
        width: widths.regular,
        maxWidth: widths.max,
      }}
      onChange={(e) =>
        handleChangeFeedback(
          e,
          state,
          dispatch,
          (event) => setFeedbackText(event.target.value),
          maxFeedbackLength
        )
      }
      value={feedbackText}
      placeholder="Enter feedback text here"
      className={`${stylePrefix}text-area`}
    />
  );
}
export default FeedbackTextArea;
