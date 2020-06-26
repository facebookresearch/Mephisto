/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import { CONNECTION_STATUS } from "mephisto-task";

function ConnectionStatusBoundary({ children, status }) {
  if (status === CONNECTION_STATUS.INITIALIZING) {
    return <div>Initializing...</div>;
  } else if (status === CONNECTION_STATUS.WEBSOCKETS_FAILURE) {
    return (
      <div>
        Sorry, but we found that your browser does not support WebSockets.
        Please consider updating your browser to a newer version or using a
        different browser and check this HIT again.
      </div>
    );
  } else if (status === CONNECTION_STATUS.FAILED) {
    return (
      <div>
        Unable to initialize. We may be having issues with our servers. Please
        refresh the page, or if that isn't working return the HIT and try again
        later if you would like to work on this task.
      </div>
    );
  } else {
    return children;
  }
}

export default ConnectionStatusBoundary;
