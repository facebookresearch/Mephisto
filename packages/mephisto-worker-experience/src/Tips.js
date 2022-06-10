import React, { useState, Fragment, useRef } from "react";
import { useOnClickOutside } from "./Hooks";
import { usePopperTooltip } from "react-popper-tooltip";

import "./index.css";
import "react-popper-tooltip/dist/styles.css";

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

  const headlessPrefix = headless ? "headless-" : "";
  const [tipData, setTipData] = useState({ header: "", body: "" });
  const tipsComponents = list.map((tip, index) => {
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
            <h1>Task Tips</h1>
            <ul
              className={`${headlessPrefix}mephisto-worker-experience-tips__tips-list`}
            >
              {tipsComponents}
            </ul>
            {!disableUserSubmission && (
              <Fragment>
                <h3>Submit A Tip</h3>
                <label
                  htmlFor={`${headlessPrefix}mephisto-worker-experience-tips__tip-header-input`}
                  className={`${headlessPrefix}mephisto-worker-experience-tips__tip-label`}
                >
                  Tip Headline:
                </label>
                <div>
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
                  <button
                    className={`${headlessPrefix}mephisto-worker-experience-tips__button`}
                    onClick={() => {
                      handleSubmit({
                        header: tipData.header,
                        text: tipData.text,
                      });
                      setTipData({ header: "", text: "" });
                    }}
                  >
                    Submit Tip
                  </button>
                </div>
              </Fragment>
            )}
          </div>
        </div>
      )}
    </Fragment>
  );
}
export default Tips;
