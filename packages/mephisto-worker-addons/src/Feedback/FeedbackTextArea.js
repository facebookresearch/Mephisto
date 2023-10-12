/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { forwardRef } from "react";
import {
  dispatchFeedbackActionNoQuestions,
  dispatchFeedbackActionWithQuestions,
  handleChangeFeedback,
} from "../Functions";
import "./index.css";

const FeedbackTextArea = forwardRef(
  (
    {
      width,
      feedbackText,
      setFeedbackText,
      stylePrefix,
      state,
      dispatch,
      maxFeedbackLength,
      id,
      containsQuestions,
      questionsFeedbackText,
      index,
      placeholder,
    },
    ref
  ) => (
    <textarea
      id={id}
      ref={ref}
      style={{
        width: `calc(${width} - 8px)`,
        boxShadow: containsQuestions
          ? ""
          : "10px 10px 23px -15px rgba(0, 0, 0, 0.26)",
      }}
      onChange={(e) => {
        handleChangeFeedback(
          e,
          () => {
            containsQuestions
              ? dispatchFeedbackActionWithQuestions(
                  e,
                  maxFeedbackLength,
                  index,
                  dispatch,
                  questionsFeedbackText
                )
              : dispatchFeedbackActionNoQuestions(
                  e,
                  maxFeedbackLength,
                  state,
                  dispatch
                );
          },
          (e) => setFeedbackText(e.target.value)
        );
      }}
      disabled={state.status === 1}
      value={feedbackText}
      placeholder={placeholder ? placeholder : "Enter feedback text here"}
      className={`${stylePrefix}text-area ${
        (containsQuestions &&
          state.status === 5 &&
          state.errorIndexes.has(index) &&
          stylePrefix + "text-area-error") ||
        (!containsQuestions &&
          state.status === 4 &&
          stylePrefix + "text-area-error")
      }`}
    />
  )
);
export default FeedbackTextArea;
