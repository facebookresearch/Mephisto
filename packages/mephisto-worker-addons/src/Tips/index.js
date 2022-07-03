import React, { useState, Fragment } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import "react-popper-tooltip/dist/styles.css";
import InfoIcon from "../InfoIcon";
import UserSubmission from "./UserSubmission";
import TaskTips from "./TaskTips";
import CloseIcon from "./CloseIcon";

function Tips({
  list,
  handleSubmit,
  disableUserSubmission,
  headless,
  maxHeight,
  width,
  placement,
  maxHeaderLength,
  maxTextLength,
}) {
  const [isVisible, setIsVisible] = useState(false);

  const maxLengths = {
    header: maxHeaderLength ? maxHeaderLength : 72,
    body: maxTextLength ? maxTextLength : 500,
  };

  const maxPopupHeight = maxHeight ? maxHeight : "30rem";
  const popupWidth = width ? width : "min(30rem, 100%)";
  const {
    getTooltipProps,
    setTooltipRef,
    setTriggerRef,
    visible,
  } = usePopperTooltip(
    {
      trigger: "click",
      closeOnOutsideClick: true,
      visible: isVisible,
      offset: [0, 25],
      onVisibleChange: setIsVisible,
    },
    {
      placement: placement ? placement : "top-start",
    }
  );
  const { taskConfig } = useMephistoTask();
  const tipsArr = (list ? list : []).concat(
    taskConfig ? taskConfig["metadata"]["tips"] : []
  );
  const headlessPrefix = headless ? "headless-" : "";
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-tips__`;
  const stylePrefixWithNoHeadlessPrefix = "mephisto-worker-addons-tips__";

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
          className={`${stylePrefixWithNoHeadlessPrefix}container`}
        >
          <div
            style={{ maxHeight: maxPopupHeight, width: popupWidth }}
            className={`${stylePrefixWithNoHeadlessPrefix}padding-container`}
          >
            <div className={`${stylePrefix}task-header-container`}>
              <h1 style={{ margin: 0 }} className={`${stylePrefix}header1`}>
                Task Tips:
              </h1>
              <button
                onClick={() => setIsVisible(false)}
                className={`${stylePrefix}close-icon-container`}
              >
                <CloseIcon />
              </button>
            </div>

            <TaskTips
              tipsArr={tipsArr}
              stylePrefix={stylePrefix}
              maxPopupHeight={maxPopupHeight}
            />
            {!disableUserSubmission && (
              <UserSubmission
                stylePrefixWithNoHeadlessPrefix={
                  stylePrefixWithNoHeadlessPrefix
                }
                stylePrefix={stylePrefix}
                handleSubmit={handleSubmit}
                maxLengths={maxLengths}
              />
            )}
          </div>
        </div>
      )}
    </Fragment>
  );
}
export default Tips;
