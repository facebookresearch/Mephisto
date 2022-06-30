import React, { useState, useEffect, useReducer } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import "./index.css";
import { feedbackReducer } from "../Reducers";
import FeedbackTextArea from "./FeedbackTextArea";
import Question from "./Question";
import SubmitButton from "./SubmitButton";

function Feedback({
  headless,
  questions,
  handleSubmit,
  textAreaWidth,
  maxTextLength,
}) {
  // To make classNames more readable
  const headlessPrefix = headless ? "headless-" : "";
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-feedback__`;
  const stylePrefixNoHeadlessPrefix = `mephisto-worker-addons-feedback__`;

  // Setting defaults
  const maxFeedbackLength = maxTextLength ? maxTextLength : 700;
  const modifiedTextAreaWidth = textAreaWidth ? textAreaWidth : "20rem";

  // For when there are questions
  const [questionsFeedbackText, setQuestionsFeedbackText] = useState([]);

  // For use when there are no questions
  const [generalFeedbackText, setGeneralFeedbackText] = useState("");
  const [state, dispatch] = useReducer(feedbackReducer, {
    status: 0,
    text: "",
    errorIndexes: null,
  });
  const containsQuestions = questions?.length > 0;
  // Configuring react-popper-tooltip
  const { getTooltipProps, setTooltipRef, setTriggerRef } = usePopperTooltip(
    {
      trigger: null,
      visible: state.status === 2 || state.status === 3,
      offset: [0, 9],
      onVisibleChange: () => {},
    },
    {
      placement: "top-start",
    }
  );

  // Setting up the questionsFeedbackText state based off of how many questions were set
  useEffect(() => {
    if (questions) setQuestionsFeedbackText(questions.map(() => ""));
  }, [questions]);

  return (
    <span
      className={`${stylePrefixNoHeadlessPrefix}container ${
        containsQuestions && `${stylePrefixNoHeadlessPrefix}vertical`
      }`}
    >
      <div className={`${stylePrefixNoHeadlessPrefix}content-container`}>
        <h1 style={{ marginTop: 0 }} className={`${stylePrefix}header1`}>
          Write Feedback
        </h1>
        <div
          className={
            containsQuestions
              ? `${stylePrefix}items-vertical`
              : `${stylePrefix}items-horizontal`
          }
        >
          {containsQuestions ? (
            questions.map((question, index) => {
              return (
                <Question
                  question={question}
                  index={index}
                  ref={setTriggerRef}
                  textAreaWidth={modifiedTextAreaWidth}
                  questionsFeedbackText={questionsFeedbackText}
                  setQuestionsFeedbackText={setQuestionsFeedbackText}
                  stylePrefix={stylePrefix}
                  state={state}
                  dispatch={dispatch}
                  maxFeedbackLength={maxFeedbackLength}
                  containsQuestions={containsQuestions}
                />
              );
            })
          ) : (
            <FeedbackTextArea
              ref={setTriggerRef}
              width={modifiedTextAreaWidth}
              feedbackText={generalFeedbackText}
              setFeedbackText={setGeneralFeedbackText}
              stylePrefix={stylePrefix}
              state={state}
              dispatch={dispatch}
              maxFeedbackLength={maxFeedbackLength}
              containsQuestions={containsQuestions}
            />
          )}

          {((!containsQuestions && state.status === 2) ||
            state.status === 3 ||
            state.status === 4) && (
            <div
              {...getTooltipProps({ className: "tooltip-container" })}
              ref={setTooltipRef}
              className={`${stylePrefixNoHeadlessPrefix}${
                state.status === 2 ? "green" : "red"
              }-box`}
            >
              {state.text}
            </div>
          )}

          <SubmitButton
            containsQuestions={containsQuestions}
            questions={questions}
            generalFeedbackText={generalFeedbackText}
            setGeneralFeedbackText={setGeneralFeedbackText}
            questionsFeedbackText={questionsFeedbackText}
            setQuestionsFeedbackText={setQuestionsFeedbackText}
            state={state}
            dispatch={dispatch}
            handleSubmit={handleSubmit}
            stylePrefix={stylePrefix}
          />

          {containsQuestions && state.status === 2 && (
            <div
              className={`${stylePrefixNoHeadlessPrefix}green-box`}
              style={{ width: modifiedTextAreaWidth }}
            >
              {state.text}
            </div>
          )}
        </div>
      </div>
    </span>
  );
}
export default Feedback;
