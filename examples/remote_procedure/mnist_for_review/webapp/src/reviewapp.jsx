/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { BaseFrontend, } from "./components/core_components.jsx";

function ReviewApp() {
  const appRef = React.useRef(null);
  const [reviewData, setReviewData] = React.useState(null);

  // Mandatory part to render review components with Task data
  window.onmessage = function (e) {
    const data = JSON.parse(e.data);
    setReviewData(data["REVIEW_DATA"]);
  };

  // Mandatory part to make review iframe with correct size of review component.
  // We cannot this automatically on our own
  React.useLayoutEffect(() => {
    function updateSize() {
      if (appRef.current) {
        window.top.postMessage(
          JSON.stringify(
            {
              IFRAME_DATA: {
                height: appRef.current.offsetHeight
              }
            }
          ),
          "*",
        )
      }
    }
    window.addEventListener("resize", updateSize);
    updateSize();
    return () => window.removeEventListener("resize", updateSize);
  }, []);

  // Do not return loading or empty components before this return,
  // we need to define `appRef` to get height of this component
  return <div ref={appRef}>
    {reviewData ? (
      <BaseFrontend
        initialTaskData={reviewData["inputs"]}
        finalResults={reviewData["outputs"]}
      />) : (
        <div>Loading...</div>
      )
    }
  </div>;
}

ReactDOM.render(<ReviewApp />, document.getElementById("app"));
