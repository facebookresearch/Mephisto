import React, { useState } from "react";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import { createFeedback } from "../Functions";

function Feedback({ headless, handleSubmit, width }) {
  const headlessPrefix = headless ? "headless-" : "";
  const [feedbackText, setFeedbackText] = useState("");
  const { taskConfig, handleMetadataSubmit } = useMephistoTask();

  return (
    <span
      style={{ width: width }}
      className="mephisto-worker-experience-feedback__container"
    >
      <input
        onChange={(e) => setFeedbackText(e.target.value)}
        value={feedbackText}
        placeholder="Enter feedback text here"
        id={`${headlessPrefix}mephisto-worker-experience-feedback__text-input`}
      />
      <button
        className={`${headlessPrefix}mephisto-worker-experience-feedback__button`}
        disabled={feedbackText.length <= 0}
        onClick={() => {
          handleMetadataSubmit(createFeedback(feedbackText));
        }}
      >
        Submit Feedback
      </button>
    </span>
  );
}
export default Feedback;
