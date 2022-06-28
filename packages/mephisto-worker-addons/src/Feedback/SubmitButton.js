import React from "react";
import { isSubmitButtonDisabled, handleFeedbackSubmit } from "../Functions";
import { useMephistoTask } from "mephisto-task";

function SubmitButton({
  containsQuestions,
  generalFeedbackText,
  questionsFeedbackText,
  state,
  dispatch,
  handleSubmit,
  stylePrefix
}) {
  const { handleMetadataSubmit } = useMephistoTask();
  return (
    <button
      className={`${stylePrefix}button`}
      disabled={isSubmitButtonDisabled(
        containsQuestions,
        generalFeedbackText,
        questionsFeedbackText,
        state
      )}
      onClick={() =>
        handleFeedbackSubmit(
          handleSubmit,
          handleMetadataSubmit,
          dispatch,
          generalFeedbackText,
          setGeneralFeedbackText
        )
      }
    >
      {state.status === 1 ? (
        <span className={`${stylePrefixNoHeadlessPrefix}loader`}></span>
      ) : (
        "Submit Feedback"
      )}
    </button>
  );
}
export default SubmitButton;
