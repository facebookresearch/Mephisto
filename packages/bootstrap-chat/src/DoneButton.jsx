/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

function DoneButton({
  onTaskComplete,
  onMessageSend,
  displayFeedback = false,
}) {
  // This component is responsible for initiating the click
  // on the mturk form's submit button.
  const [showFeedback, setShowFeedback] = React.useState(displayFeedback);
  const [feedbackGiven, setFeedbackGiven] = React.useState(null);

  let review_flow = null;
  let done_button = (
    <button
      id="done-button"
      type="button"
      className="btn btn-primary btn-lg"
      onClick={() => onTaskComplete()}
    >
      <span className="glyphicon glyphicon-ok-circle" aria-hidden="true" /> Done
      with this HIT
    </button>
  );
  if (displayFeedback) {
    if (showFeedback) {
      review_flow = (
        <ReviewButtons
          initState={undefined}
          onMessageSend={onMessageSend}
          onChoice={(did_give) => {
            setShowFeedback(false);
            setFeedbackGiven(did_give);
          }}
        />
      );
      done_button = null;
    } else if (feedbackGiven) {
      review_flow = <span>Thanks for the feedback!</span>;
    }
  }
  return (
    <div>
      {review_flow}
      <div>{done_button}</div>
    </div>
  );
}

export default DoneButton;
