import React, { useState, useEffect, useReducer, useRef } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import { handleFeedbackSubmit } from "../Functions";
import { feedbackReducer } from "../Reducers";
import FeedbackTextArea from "./FeedbackTextArea";

function Feedback({
  headless,
  questions,
  handleSubmit,
  textAreaWidth,
  textAreaMinWidth,
  textAreaMaxWidth,
  maxTextLength,
  width,
}) {
  const headlessPrefix = headless ? "headless-" : "";
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-feedback__`;
  const stylePrefixNoHeadlessPrefix = `mephisto-worker-addons-feedback__`;
  const maxFeedbackLength = maxTextLength ? maxTextLength : 700;
  const handleMetadataSubmit = useMephistoTask();
  const [feedbackText, setFeedbackText] = useState("");
  const [state, dispatch] = useReducer(feedbackReducer, {
    status: 0,
    text: "",
  });
  const containsQuestions = questions?.length > 0;
  const textAreaWidths = {
    min: textAreaMinWidth ? textAreaMinWidth : "",
    regular: textAreaWidth ? textAreaWidth : "22rem",
    max: textAreaMaxWidth ? textAreaMaxWidth : "27rem",
  };
  const updateSizeRef = useRef(null);
  const { getTooltipProps, setTooltipRef, setTriggerRef, update } =
    usePopperTooltip(
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

  // Used to make tooltip stay in correct position even if text area size is dragged
  const observer = useRef(null);
  useEffect(() => {
    if (updateSizeRef && updateSizeRef.current) {
      observer.current = new ResizeObserver((entries) => {
        if (update) update();
      });
      observer.current.observe(updateSizeRef.current);
      return () => {
        observer.current.unobserve(updateSizeRef.current);
      };
    }
  }, [observer, updateSizeRef, update]);

  return (
    <span
      style={{ minWidth: textAreaWidths.regular }}
      className={`${stylePrefixNoHeadlessPrefix}container ${
        containsQuestions && "vertical"
      }`}
    >
      <span
        style={{ minWidth: textAreaWidths.regular }}
        ref={updateSizeRef}
        className={`${stylePrefixNoHeadlessPrefix}${
          containsQuestions
            ? "text-area-container-vertical"
            : "text-area-container"
        }`}
      >
        {containsQuestions ? (
          questions.map((question, index) => {
            return (
              <div
                className={`${stylePrefix}questions-container`}
                key={`question-${index}`}
              >
                <label
                  style={{ width: textAreaWidths.regular }}
                  className={`${stylePrefix}question`}
                  htmlFor={`question-${index}`}
                >
                  {question}
                </label>{" "}
                <FeedbackTextArea
                  id={`question-${index}`}
                  setTriggerRef={setTriggerRef}
                  widths={textAreaWidths}
                  feedbackText={feedbackText}
                  setFeedbackText={setFeedbackText}
                  stylePrefix={stylePrefix}
                  state={state}
                  dispatch={dispatch}
                  maxFeedbackLength={maxFeedbackLength}
                />
              </div>
            );
          })
        ) : (
          <FeedbackTextArea
            setTriggerRef={setTriggerRef}
            widths={textAreaWidths}
            feedbackText={feedbackText}
            setFeedbackText={setFeedbackText}
            stylePrefix={stylePrefix}
            state={state}
            dispatch={dispatch}
            maxFeedbackLength={maxFeedbackLength}
          />
        )}
      </span>

      {(state.status === 2 || state.status === 3 || state.status === 4) && (
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
      <button
        className={`${stylePrefix}button`}
        disabled={
          feedbackText.length <= 0 || state.status === 1 || state.status === 4
        }
        onClick={() =>
          handleFeedbackSubmit(
            handleSubmit,
            handleMetadataSubmit,
            dispatch,
            feedbackText,
            setFeedbackText
          )
        }
      >
        {state.status === 1 ? (
          <span className="loader"></span>
        ) : (
          "Submit Feedback"
        )}
      </button>
    </span>
  );
}
export default Feedback;
