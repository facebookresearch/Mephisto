import React, { useState, Fragment, useReducer } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { handleChangeTip, handleTipSubmit } from "../Functions";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import "react-popper-tooltip/dist/styles.css";
import { tipReducer } from "../Reducers";
import InfoIcon from "./InfoIcon";

function Tips({
  list,
  handleSubmit,
  disableUserSubmission,
  headless,
  maxHeight,
  maxWidth,
  placement,
  maxHeaderLength,
  maxTextLength,
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [state, dispatch] = useReducer(tipReducer, {
    status: 0,
    text: "",
  });

  const maxLengths = {
    header: maxHeaderLength ? maxHeaderLength : 72,
    body: maxTextLength ? maxTextLength : 500,
  };

  const maxPopupHeight = maxHeight ? maxHeight : "30rem";
  const maxPopupWidth = maxWidth ? maxWidth : "30rem";
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
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-tips__`;

  const [tipData, setTipData] = useState({ header: "", text: "" });
  const tipsComponents = tipsArr.map((tip, index) => {
    return (
      <li key={`tip-${index + 1}`} className={`${stylePrefix}tip`}>
        <h2 className={`${stylePrefix}tip-header2`}>{tip.header}</h2>
        <p className={`${stylePrefix}tip-text`}>{tip.text}</p>
      </li>
    );
  });

  return (
    <Fragment>
      <button
        ref={setTriggerRef}
        onClick={() => setIsVisible(!isVisible)}
        className={`${stylePrefix}button ${stylePrefix}no-margin`}
      >
        <InfoIcon margin="0 0.225rem 0 0" />
        {visible ? "Hide Tips" : "Show Tips"}
      </button>
      {visible && (
        <div
          {...getTooltipProps({ className: "tooltip-container" })}
          ref={setTooltipRef}
          className={`mephisto-worker-addons-tips__container`}
        >
          <div
            className={`mephisto-worker-addons-tips__padding_container`}
            style={{ maxHeight: maxPopupHeight, maxWidth: maxPopupWidth }}
          >
            <h1 className={`${stylePrefix}tip-header1`}>Task Tips:</h1>
            <ul
              style={{ maxHeight: `calc(${maxPopupHeight}/2)` }}
              className={`${stylePrefix}tips-list`}
            >
              {tipsArr.length <= 0 ? (
                <li className={`${stylePrefix}tip`}>
                  <h2
                    className={`${stylePrefix}tip-header2  ${stylePrefix}no-margin`}
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
                <h1 className={`${stylePrefix}tip-header1`}>Submit A Tip: </h1>
                <label
                  htmlFor={`${stylePrefix}tip-header-input`}
                  className={`${stylePrefix}tip-label`}
                >
                  Tip Headline:
                </label>
                <input
                  id={`${stylePrefix}tip-header-input`}
                  placeholder="Write your tip's headline here..."
                  value={tipData.header}
                  onChange={(e) =>
                    handleChangeTip(
                      e,
                      tipData,
                      dispatch,
                      () =>
                        setTipData({
                          header: e.target.value,
                          text: tipData.text,
                        }),
                      maxLengths
                    )
                  }
                />

                <label
                  htmlFor={`${stylePrefix}tip-text-input`}
                  className={`${stylePrefix}tip-label`}
                >
                  Tip Body:
                </label>
                <textarea
                  placeholder="Write your tip body here..."
                  id={`${stylePrefix}tip-text-input`}
                  value={tipData.text}
                  onChange={(e) =>
                    handleChangeTip(
                      e,
                      tipData,
                      dispatch,
                      () =>
                        setTipData({
                          header: tipData.header,
                          text: e.target.value,
                        }),
                      maxLengths
                    )
                  }
                />
                {(state.status === 2 ||
                  state.status === 3 ||
                  state.status === 4 ||
                  state.status === 5) && (
                  <div
                    className={`${stylePrefix}${
                      state.status === 2 ? "green" : "red"
                    }-box`}
                  >
                    {state.text}
                  </div>
                )}
                <button
                  disabled={
                    state.status === 1 ||
                    state.status === 4 ||
                    state.status === 5 ||
                    tipData.text.length === 0 ||
                    tipData.header.length === 0
                  }
                  className={`${stylePrefix}button`}
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
