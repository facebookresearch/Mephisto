import React, { useState, Fragment, useRef } from "react";
import { useOnClickOutside } from "./hooks";
import { usePopper } from "react-popper";
import "./index.css";

function Tips({ list, handleSubmit, disableUserSubmission, headless }) {
  const [isVisible, setIsVisible] = useState(false);
  const referenceRef = useRef(null);
  const popperRef = useRef(null);
  useOnClickOutside([popperRef, referenceRef], () => setIsVisible(false));

  const { styles, attributes } = usePopper(
    referenceRef.current,
    popperRef.current,
    {
      placement: "top",
      modifiers: [
        {
          name: "offset",
          options: {
            offset: [8, 15],
          },
        },
      ],
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
        ref={referenceRef}
        onClick={() => setIsVisible(!isVisible)}
        className={`${headlessPrefix}mephisto-worker-experience-tips__button`}
      >
        {isVisible ? "Hide Tips" : "Show Tips"}
      </button>
      <div
        ref={popperRef}
        style={styles.popper}
        {...attributes.popper}
        className={`mephisto-worker-experience-tips__container mephisto-worker-experience-tips__${
          isVisible ? "showing" : "hiding"
        }`}
      >
        <div className="mephisto-worker-experience-tips__padding-container">
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
                    setTipData({ header: tipData.header, text: e.target.value })
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

      <div className="test-box"></div>
      <div className="test-box"></div>
      <div className="test-box"></div>
      <div className="test-box"></div>
      <div className="test-box"></div>
    </Fragment>
  );
}
export default Tips;
