import React, { useState } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { useMephistoTask } from "mephisto-task";
import root from "react-shadow";
import tipsStyles from "!raw-loader!./index.css";
import "react-popper-tooltip/dist/styles.css";
import InfoIcon from "./InfoIcon";
import UserSubmission from "./UserSubmission";
import TaskTips from "./TaskTips";
import CloseIcon from "./CloseIcon";
import { getTipsArr } from "../Functions";

function TipsContainer({ headless, children }) {
  if (headless) {
    return <div>{children}</div>;
  } else {
    return <root.div>{children}</root.div>;
  }
}

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
  const popupWidth = width ? width : "30rem";
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
      offset: [0, 18],
      onVisibleChange: setIsVisible,
    },
    {
      placement: placement ? placement : "top-start",
    }
  );
  const { taskConfig } = useMephistoTask();
  const tipsArr = getTipsArr(list, taskConfig);
  const headlessPrefix = headless ? "headless-" : "";
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-tips__`;
  const stylePrefixWithNoHeadlessPrefix = "mephisto-worker-addons-tips__";

  return (
    <TipsContainer headless={headless}>
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
            className={`${stylePrefixWithNoHeadlessPrefix}padding-container`}
            style={{ maxHeight: maxPopupHeight, width: popupWidth }}
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
      <style type="text/css">{tipsStyles}</style>
    </TipsContainer>
  );
}
export default Tips;
