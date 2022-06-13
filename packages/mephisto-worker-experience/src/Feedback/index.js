import React, { useState, useReducer } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import { handleFeedbackSubmit, handleChangeFeedback } from "../Functions";
import { feedbackReducer } from "../Reducers";

function Feedback({ headless, handleSubmit, width }) {
  const headlessPrefix = headless ? "headless-" : "";
  const [feedbackText, setFeedbackText] = useState("");
  const { handleMetadataSubmit } = useMephistoTask();
  const [state, dispatch] = useReducer(feedbackReducer, {
    status: 0,
    text: "",
  });
  const maxFeedbackLength = 3000;
  const { getTooltipProps, setTooltipRef, setTriggerRef, visible } =
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

  return (
    <span
      style={{ width: width }}
      className="mephisto-worker-experience-feedback__container"
    >
      <textarea
        ref={setTriggerRef}
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
        id={`${headlessPrefix}mephisto-worker-experience-feedback__text-area`}
      />
      {(state.status === 2 || state.status === 3 || state.status === 4) && (
        <div
          {...getTooltipProps({ className: "tooltip-container" })}
          ref={setTooltipRef}
          className={`mephisto-worker-experience-feedback__${
            state.status === 2 ? "green" : "red"
          }-box`}
        >
          {state.text}
        </div>
      )}
      <button
        className={`${headlessPrefix}mephisto-worker-experience-feedback__button`}
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
