import React, { Fragment } from "react";

function TaskTips({ tipsArr, stylePrefix, tipsComponents }) {
  return (
    <Fragment>
      {tipsArr.length <= 0 ? (
        <li className={`${stylePrefix}tip`}>
          <h2 className={`${stylePrefix}tip-header2  ${stylePrefix}no-margin`}>
            There are no submitted tips!
          </h2>
        </li>
      ) : (
        tipsComponents
      )}
    </Fragment>
  );
}
export default TaskTips;
