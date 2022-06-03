import React, { Fragment, useState } from "react";
import "./index.css";

function Tips({ list, handleSubmit, disableUserSubmission }) {
  const [tipData, setTipData] = useState({ header: "", body: "" });
  const tipsComponents = list.map((tip, index) => {
    return (
      <li key={`tip-${index + 1}`} className="tip">
        <h2 className="tip-header">{tip.header}</h2>
        <p>{tip.text}</p>
      </li>
    );
  });

  return (
    <div>
      <ul className="tips-list">{tipsComponents}</ul>
      {!disableUserSubmission && (
        <Fragment>
          <label htmlFor="tip-headline" className="tip-label">
            Tip Headline:
          </label>
          <input
            id="tip-headline"
            placeholder="Write your tip's headline here..."
            onBlur={(e) =>
              setTipData({ header: e.target.value, body: tipData.body })
            }
          />
          <label htmlFor="tip-body" className="tip-label">
            Tip Body:
          </label>
          <textarea
            placeholder="Write your tip body here..."
            id="tip-body"
            onBlur={(e) =>
              setTipData({ header: tipData.header, body: e.target.value })
            }
          />
          <button
            className="submit-button"
            onClick={() =>
              handleSubmit({ header: tipData.header, body: tipData.body })
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
