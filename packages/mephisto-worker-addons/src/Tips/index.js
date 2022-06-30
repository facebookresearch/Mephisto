import React, { useState, Fragment } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import { useMephistoTask } from "mephisto-task";
import "./index.css";
import "react-popper-tooltip/dist/styles.css";
import InfoIcon from "../InfoIcon";
import UserSubmission from "./UserSubmission";
import TaskTips from "./TaskTips";

function Tips({
  list,
  handleSubmit,
  disableUserSubmission,
  headless,
  maxHeight,
  width,
  placement,
}) {
  const [isVisible, setIsVisible] = useState(false);

  const maxPopupHeight = maxHeight ? maxHeight : "30rem";
  const popupWidth = width ? width : "30rem";

  // This is to configure react-popper-tooltip
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
      offset: [0, 6],
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

  // These exist to help make reading classnames easier
  const headlessPrefix = headless ? "headless-" : "";
  const stylePrefix = `${headlessPrefix}mephisto-worker-addons-tips__`;

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
          className={`${stylePrefix}container`}
        >
          <div
            className={`${stylePrefix}padding_container`}
            style={{ maxHeight: maxPopupHeight, width: popupWidth }}
          >
            <h1 style={{ marginTop: 0 }} className={`${stylePrefix}header1`}>
              Task Tips:
            </h1>
            <TaskTips
              tipsArr={tipsArr}
              stylePrefix={stylePrefix}
              maxPopupHeight={maxPopupHeight}
            />

            {!disableUserSubmission && (
              <UserSubmission
                stylePrefix={stylePrefix}
                handleSubmit={handleSubmit}
              />
            )}
          </div>
        </div>
      )}
    </Fragment>
  );
}
export default Tips;
