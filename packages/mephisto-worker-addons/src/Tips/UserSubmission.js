import React, { Fragment, useState, useReducer } from "react";
import { handleTipSubmit, handleChangeTip } from "../Functions";
import { tipReducer } from "../Reducers";
import { useMephistoTask } from "mephisto-task";

function UserSubmission({
  stylePrefixWithNoHeadlessPrefix,
  stylePrefix,
  handleSubmit,
  maxLengths,
}) {
  const [tipData, setTipData] = useState({ header: "", text: "" });
  const { handleMetadataSubmit } = useMephistoTask();
  const [state, dispatch] = useReducer(tipReducer, {
    status: 0,
    text: "",
  });

  return (
    <Fragment>
      <h1 className={`${stylePrefix}header1`}>Submit A Tip: </h1>
      <label
        htmlFor={`${stylePrefix}header-input`}
        className={`${stylePrefix}label`}
      >
        Tip Headline:
      </label>
      <input
        id={`${stylePrefix}header-input`}
        className={state.status == 4 ? `${stylePrefix}input-error` : undefined}
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
        disabled={state.status === 1}
      />

      <label
        htmlFor={`${stylePrefix}text-input`}
        className={`${stylePrefix}label`}
      >
        Tip Body:
      </label>
      <textarea
        placeholder="Write your tip body here..."
        id={`${stylePrefix}text-input`}
        className={state.status == 5 ? `${stylePrefix}input-error` : undefined}
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
        disabled={state.status === 1}
      />
      {(state.status === 2 ||
        state.status === 3 ||
        state.status === 4 ||
        state.status === 5) && (
        <div
          className={`${stylePrefixWithNoHeadlessPrefix}${
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
          <span className={`${stylePrefixWithNoHeadlessPrefix}loader`}></span>
        ) : (
          "Submit Tip"
        )}
      </button>
    </Fragment>
  );
}
export default UserSubmission;
