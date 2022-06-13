import React, { useState, Fragment, useReducer } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { handleTipSubmit } from "../Functions";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import "react-popper-tooltip/dist/styles.css";
import { tipsReducer } from "../Reducers";
import InfoIcon from "./InfoIcon";

function Tips({
  list,
  handleSubmit,
  disableUserSubmission,
  headless,
  maxHeight,
  maxWidth,
  placement,
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [state, dispatch] = useReducer(tipsReducer, {
    status: 0,
    text: "",
  });

  const { getTooltipProps, setTooltipRef, setTriggerRef, visible } =
    usePopperTooltip(
      {
        trigger: "click",
        closeOnOutsideClick: true,
        visible: isVisible,
        offset: [0, 6],
        onVisibleChange: setIsVisible,
      },
      {
        placement: placement ? placement : "top-start",
      }
    );

  const { taskConfig, handleMetadataSubmit } = useMephistoTask();
  const tipsArr = (list ? list : []).concat(
    taskConfig ? taskConfig["metadata"]["tips"] : []
  );
  const headlessPrefix = headless ? "headless-" : "";
  const [tipData, setTipData] = useState({ header: "", text: "" });
  const tipsComponents = tipsArr.map((tip, index) => {
    return (
      <li
        key={`tip-${index + 1}`}
        className={`${headlessPrefix}mephisto-worker-experience-tips__tip`}
      >
        <h2
          className={`${headlessPrefix}mephisto-worker-experience-tips__tip-header2`}
        >
          {tip.header}
        </h2>
        <p>{tip.text}</p>
      </li>
    );
  });

  return (
    <Fragment>
      <button
        ref={setTriggerRef}
        onClick={() => setIsVisible(!isVisible)}
        className={`${headlessPrefix}mephisto-worker-experience-tips__button`}
      >
        <InfoIcon margin="0 0.225rem 0 0" />
        {visible ? "Hide Tips" : "Show Tips"}
      </button>
      {visible && (
        <div
          {...getTooltipProps({ className: "tooltip-container" })}
          ref={setTooltipRef}
          className={`mephisto-worker-experience-tips__container`}
        >
          <div
            className="mephisto-worker-experience-tips__padding_container"
            style={{ maxHeight: maxHeight, maxWidth: maxWidth }}
          >
            <h1>Task Tips:</h1>
            <ul
              className={`${headlessPrefix}mephisto-worker-experience-tips__tips-list`}
            >
              {tipsArr.length <= 0 ? (
                <li
                  className={`${headlessPrefix}mephisto-worker-experience-tips__tip`}
                >
                  <h2
                    className={`${headlessPrefix}mephisto-worker-experience-tips__tip-header2`}
                  >
                    There are no submitted tips!
                  </h2>
                </li>
              ) : (
                tipsComponents
              )}
            </ul>
            {!disableUserSubmission && (
              <Fragment>
                <h1>Submit A Tip: </h1>
                <label
                  htmlFor={`${headlessPrefix}mephisto-worker-experience-tips__tip-header-input`}
                  className={`${headlessPrefix}mephisto-worker-experience-tips__tip-label`}
                >
                  Tip Headline:
                </label>
                <input
                  id={`${headlessPrefix}mephisto-worker-experience-tips__tip-header-input`}
                  placeholder="Write your tip's headline here..."
                  value={tipData.header}
                  onChange={(e) =>
                    setTipData({ header: e.target.value, text: tipData.text })
                  }
                />

                <label
                  htmlFor={`${headlessPrefix}mephisto-worker-experience-tips__tip-text-input`}
                  className={`${headlessPrefix}mephisto-worker-experience-tips__tip-label`}
                >
                  Tip Body:
                </label>
                <textarea
                  placeholder="Write your tip body here..."
                  id={`${headlessPrefix}mephisto-worker-experience-tips__tip-text-input`}
                  value={tipData.text}
                  onChange={(e) =>
                    setTipData({
                      header: tipData.header,
                      text: e.target.value,
                    })
                  }
                />
                {(state.status === 2 || state.status === 3) && (
                  <div
                    className={`mephisto-worker-experience-tips__${
                      state.status === 2 ? "green" : "red"
                    }-box`}
                  >
                    {state.text}
                  </div>
                )}
                <button
                  disabled={
                    state.status === 1 ||
                    tipData.text.length === 0 ||
                    tipData.header.length === 0
                  }
                  className={`${headlessPrefix}mephisto-worker-experience-tips__button`}
                  onClick={() =>
                    handleTipSubmit(
                      handleSubmit,
                      handleMetadataSubmit,
                      dispatch,
                      tipData,
                      setTipData
                    )
                  }
                >
                  {state.status === 1 ? (
                    <span className="loader"></span>
                  ) : (
                    "Submit Tip"
                  )}
                </button>
              </Fragment>
            )}
          </div>
        </div>
      )}
    </Fragment>
  );
}
export default Tips;
