/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { isSubmitButtonDisabled, handleFeedbackSubmit } from "../Functions";
import { useMephistoTask } from "mephisto-task";

function SubmitButton({
  containsQuestions,
  generalFeedbackText,
  setGeneralFeedbackText,
  questionsFeedbackText,
  setQuestionsFeedbackText,
  state,
  dispatch,
  handleSubmit,
  stylePrefix,
  questions,
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
          setGeneralFeedbackText,
          questionsFeedbackText,
          setQuestionsFeedbackText,
          questions,
          containsQuestions
        )
      }
    >
      {state.status === 1 ? (
        <span className={`mephisto-worker-addons-feedback__loader`}></span>
      ) : (
        "Submit Feedback"
      )}
    </button>
  );
}
export default SubmitButton;
