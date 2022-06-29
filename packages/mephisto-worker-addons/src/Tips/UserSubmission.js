import React, { Fragment, useState, useReducer } from "react";
import { handleTipSubmit, handleChangeTip } from "../Functions";
import { tipReducer } from "../Reducers";
import { useMephistoTask } from "mephisto-task";

function UserSubmission({ stylePrefix, handleSubmit, maxLengths }) {
  const [tipData, setTipData] = useState({ header: "", text: "" });
  const { handleMetadataSubmit } = useMephistoTask();
  const [state, dispatch] = useReducer(tipReducer, {
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
          <span className="mephisto-worker-addons-tips__loader"></span>
        ) : (
          "Submit Tip"
        )}
      </button>
    </Fragment>
  );
}
export default UserSubmission;
