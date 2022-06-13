import React, { useState } from "react";
import "./index.css";

function Feedback({ headless, handleSubmit, width }) {
  const headlessPrefix = headless ? "headless-" : "";
  const [feedbackText, setFeedbackText] = useState("");

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
      >
        Submit Feedback
      </button>
    </span>
  );
}
export default Feedback;
