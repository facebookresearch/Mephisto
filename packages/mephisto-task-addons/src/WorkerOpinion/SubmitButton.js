/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { useMephistoTask } from "mephisto-task-multipart";
import React from "react";
import { handleWorkerOpinionSubmit, isSubmitButtonDisabled } from "./Functions";

function SubmitButton({
  containsQuestions,
  dispatch,
  generalText,
  handleSubmit,
  questions,
  questionsTexts,
  setAttachmentsNames,
  setAttachmentsValue,
  setGeneralText,
  setQuestionsTexts,
  state,
  stylePrefix,
}) {
  const { handleMetadataSubmit } = useMephistoTask();
  return (
    <button
      className={`${stylePrefix}button btn btn-primary btn-sm`}
      disabled={isSubmitButtonDisabled(
        containsQuestions,
        generalText,
        questionsTexts,
        state
      )}
      onClick={() =>
        handleWorkerOpinionSubmit(
          handleSubmit,
          handleMetadataSubmit,
          dispatch,
          generalText,
          setGeneralText,
          questionsTexts,
          setQuestionsTexts,
          questions,
          containsQuestions,
          setAttachmentsNames,
          setAttachmentsValue
        )
      }
    >
      {state.status === 1 ? (
        <span className={`${stylePrefix}loader`}></span>
      ) : (
        "Submit opinion"
      )}
    </button>
  );
}

export default SubmitButton;
