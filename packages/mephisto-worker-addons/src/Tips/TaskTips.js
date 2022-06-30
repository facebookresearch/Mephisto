import React from "react";

function TaskTips({ tipsArr, stylePrefix, maxPopupHeight }) {
  const tipsComponents = tipsArr.map((tip, index) => {
    return (
      <li key={`tip-${index + 1}`} className={`${stylePrefix}tip`}>
        <h2 className={`${stylePrefix}header2`}>{tip.header}</h2>
        <p className={`${stylePrefix}text`}>{tip.text}</p>
      </li>
    );
  });
  return (
    <ul
      style={{ maxHeight: `calc(${maxPopupHeight}/2)` }}
      className={`${stylePrefix}list`}
    >
      {tipsArr.length > 0 ? (
        tipsComponents
      ) : (
        <h2 className={`${stylePrefix}header2  ${stylePrefix}no-submissions`}>
          There are no submitted tips!
        </h2>
      )}
    </ul>
  );
}
export default TaskTips;
