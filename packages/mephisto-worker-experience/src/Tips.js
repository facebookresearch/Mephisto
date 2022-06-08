import React, { Fragment, useState } from "react";
import "./index.css";

function Tips({ list, handleSubmit, disableUserSubmission, headless }) {
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
    <div
      className={`${headlessPrefix}mephisto-worker-experience-tips-container`}
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
              onBlur={(e) =>
                setTipData({ header: e.target.value, text: tipData.text })
              }
            />
          </div>

          <label
            htmlFor={`${headlessPrefix}mephisto-worker-experience-tips__tip-text-input`}
            className={`${headlessPrefix}mephisto-worker-experience-tips__tip-label`}
          >
            Tip Body:
          </label>
          <textarea
            placeholder="Write your tip body here..."
            id={`${headlessPrefix}mephisto-worker-experience-tips__tip-text-input`}
            onBlur={(e) =>
              setTipData({ header: tipData.header, text: e.target.value })
            }
          />
          <button
            className={`${headlessPrefix}mephisto-worker-experience-tips__submit-button`}
            onClick={() =>
              handleSubmit({ header: tipData.header, text: tipData.text })
            }
          >
            Submit Tip
          </button>
        </Fragment>
      )}
    </div>
  );
}
export default Tips;
