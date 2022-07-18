import React, { useState, useEffect, useReducer } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import root from "react-shadow";
import feedbackStyles from "!raw-loader!./index.css";
import { feedbackReducer } from "../Reducers";
import FeedbackTextArea from "./FeedbackTextArea";
import Question from "./Question";
import SubmitButton from "./SubmitButton";

function FeedbackContainer({ headless, children }) {
  if (headless) {
    return <div>{children}</div>;
  } else {
    return <root.div>{children}</root.div>;
  }
}

function Feedback({
  headless,
  questions,
  handleSubmit,
  maxTextLength,
  textAreaWidth,
}) {
  // To make classNames more readable
  const headlessPrefix = headless ? "headless-" : "";
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-feedback__`;
  const stylePrefixNoHeadlessPrefix = `mephisto-worker-addons-feedback__`;

  // Setting defaults
  const maxFeedbackLength = maxTextLength ? maxTextLength : 700;
  const modifiedTextAreaWidth = textAreaWidth ? textAreaWidth : "100%";
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
      offset: [0, 18],
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
    <FeedbackContainer headless={headless}>
      <div
        className={`${stylePrefixNoHeadlessPrefix}container ${stylePrefixNoHeadlessPrefix}vertical`}
      >
        <header className={`${stylePrefix}header-items`}>
          <h1 style={{ margin: 0 }} className={`${stylePrefix}header1`}>
            Write Feedback
          </h1>
          <p className={`${stylePrefix}subtitle`}> (optional)</p>
        </header>

        <section
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
                  key={`question-${index}`}
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
                  placeholder="Answer the above question here"
                />
              );
            })
          ) : (
            <FeedbackTextArea
              id={`${stylePrefixNoHeadlessPrefix}solo-input`}
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
              className={`${stylePrefix}${
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
        </section>
      </div>
      <style type="text/css">{feedbackStyles}</style>
    </FeedbackContainer>
  );
}
export default Feedback;
