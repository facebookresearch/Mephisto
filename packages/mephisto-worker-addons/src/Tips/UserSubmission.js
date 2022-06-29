import React, { Fragment, useState, useReducer } from "react";
import { handleTipSubmit } from "../Functions";
import { tipsReducer } from "../Reducers";
import { useMephistoTask } from "mephisto-task";

function UserSubmission({ stylePrefix, handleSubmit }) {
  const [tipData, setTipData] = useState({ header: "", text: "" });
  const { handleMetadataSubmit } = useMephistoTask();
  const [state, dispatch] = useReducer(tipsReducer, {
    status: 0,
    text: "",
  });

  return (
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
          setTipData({ header: e.target.value, text: tipData.text })
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
          setTipData({
            header: tipData.header,
            text: e.target.value,
          })
        }
      />
      {(state.status === 2 || state.status === 3) && (
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
          <span className="mephisto-worker-addons-tips__loader"></span>
        ) : (
          "Submit Tip"
        )}
      </button>
    </Fragment>
  );
}
export default UserSubmission;
