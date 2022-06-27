import React, { useState, useEffect, useReducer, useRef } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import { handleFeedbackSubmit, handleChangeFeedback } from "../Functions";
import { feedbackReducer } from "../Reducers";

function Feedback({ headless, handleSubmit, width, maxTextLength }) {
  const headlessPrefix = headless ? "headless-" : "";
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-feedback__`;
  const stylePrefixNoHeadlessPrefix = `mephisto-worker-addons-feedback__`;
  const maxFeedbackLength = maxTextLength ? maxTextLength : 700;

  const [feedbackText, setFeedbackText] = useState("");
  const { handleMetadataSubmit } = useMephistoTask();
  const [state, dispatch] = useReducer(feedbackReducer, {
    status: 0,
    text: "",
  });

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
    <span className={`${stylePrefixNoHeadlessPrefix}container`}>
      <span
        ref={updateSizeRef}
        className={`${stylePrefixNoHeadlessPrefix}text-area-container`}
      >
        <textarea
          ref={setTriggerRef}
          style={{
            minWidth: width ? width : "18rem",
            width: width ? width : "18rem",
          }}
          onChange={(e) =>
            handleChangeFeedback(
              e,
              state,
              dispatch,
              (event) => setFeedbackText(event.target.value),
              maxFeedbackLength
            )
          }
          value={feedbackText}
          placeholder="Enter feedback text here"
          id={`${stylePrefix}text-area`}
        />
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
