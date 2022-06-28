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
    },
    ref
  ) => (
    <textarea
      id={id}
      ref={ref}
      style={{ width: width }}
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
      value={feedbackText}
      placeholder="Enter feedback text here"
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
