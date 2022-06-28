import React, { forwardRef } from "react";
import FeedbackTextArea from "./FeedbackTextArea";

const Question = forwardRef(
  (
    {
      question,
      index,
      textAreaWidth,
      questionsFeedbackText,
      setQuestionsFeedbackText,
      stylePrefix,
      state,
      dispatch,
      maxFeedbackLength,
    },
    ref
  ) => (
    <div
      className={`${stylePrefix}questions-container`}
      key={`question-${index}`}
    >
      <label
        style={{ width: textAreaWidth }}
        className={`${stylePrefix}question`}
        htmlFor={`question-${index}`}
      >
        {question}
      </label>{" "}
      <FeedbackTextArea
        id={`question-${index}`}
        ref={ref}
        index={index}
        width={textAreaWidth}
        questionsFeedbackText={questionsFeedbackText}
        feedbackText={questionsFeedbackText[index]}
        setFeedbackText={(textValue) => {
          const tempQuestionsFeedback = [...questionsFeedbackText];
          tempQuestionsFeedback[index] = textValue;
          setQuestionsFeedbackText(tempQuestionsFeedback);
        }}
        stylePrefix={stylePrefix}
        state={state}
        dispatch={dispatch}
        maxFeedbackLength={maxFeedbackLength}
        containsQuestions
      />
      {state.status === 5 && state.errorIndexes.has(index) && (
        <div
          className="mephisto-worker-addons-feedback__red-box"
          style={{ width: textAreaWidth }}
        >
          {state.text}
        </div>
      )}
    </div>
  )
);

export default Question;
