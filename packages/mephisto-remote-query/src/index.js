/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import ConnectionIndicator from "./ConnectionIndicator.jsx";
import {
  useMephistoLiveTask,
  AGENT_STATUS,
  STATUS_TO_TEXT_MAP,
  MephistoContext,
  ErrorBoundary,
} from "mephisto-task";

// Generate a random id
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

const useMephistoRemoteQueryTask = function (props) {
  // mapping of request ID to the callback object
  const [requestCallbacks, addRequestCallback] = React.useReducer(
    (previousRequestCallbacks, newRequestCallback) => {
      let requestId = newRequestCallback.request_id;
      let newRequestCallbacks = {
        ...previousRequestCallbacks,
        [requestId]: newRequestCallback,
      };
      return newRequestCallbacks;
    },
    {}
  );

  const [disconnectIssueText, setDisconnectIssueText] = React.useState();

  // We register a ref so that the liveUpdate handler has access
  // to the current set of callbacks
  const requestCallbacksRef = React.useRef();
  requestCallbacksRef.current = requestCallbacks;

  function handleRemoteResponse(liveUpdate) {
    let targetRequest = requestCallbacksRef.current[liveUpdate.handles];
    if (targetRequest === undefined) {
      console.log("No request found to handle this live update", liveUpdate);
      return;
    }

    let parsedResponse = JSON.parse(liveUpdate.response);
    targetRequest.callback({
      requestId: targetRequest.request_id,
      response: parsedResponse,
      args: targetRequest.args,
    });
  }

  let mephistoProps = useMephistoLiveTask({
    onStatusUpdate: ({ status }) => {
      if (
        [
          AGENT_STATUS.DISCONNECT,
          AGENT_STATUS.RETURNED,
          AGENT_STATUS.EXPIRED,
          AGENT_STATUS.TIMEOUT,
          AGENT_STATUS.MEPHISTO_DISCONNECT,
        ].includes(status)
      ) {
        setDisconnectIssueText(STATUS_TO_TEXT_MAP[status]);
      }
    },
    onLiveUpdate: (liveUpdate) => {
      handleRemoteResponse(liveUpdate);
    },
  });

  // We remove the live socket props, as we intend to provide a different interface
  let {
    connect,
    destroy,
    sendLiveUpdate,
    ...otherMephistoProps
  } = mephistoProps;
  let { agentId } = mephistoProps;

  // They're still exposed in a separate manner though
  const _fullSocketProps = {
    connect,
    destroy,
    sendLiveUpdate,
  };

  React.useEffect(() => {
    if (agentId) {
      console.log("connecting...");
      connect(agentId);
    }
  }, [agentId]);

  const makeRemoteCall = React.useCallback(
    // Takes in a remote call to send, as well as an optional callback
    // for the response. Returns the requestId for this request.
    //
    // The argument format is the targetEvent string, a json serializable set of
    // arguments for the targetEvent, and an optional callback
    //
    // The callback format will be called with the requestId for the original
    // request, the returned data, and the input data as arguments.
    ({ targetEvent, args, callback }) => {
      const requestId = uuidv4();
      let liveUpdate = {
        request_id: requestId,
        target: targetEvent,
        args: JSON.stringify(args),
      };
      sendLiveUpdate(liveUpdate).then((updatePacket) => {
        if (callback !== undefined) {
          updatePacket.callback = callback;
          updatePacket.args = args;
          addRequestCallback(updatePacket);
        }
      });
      return requestId;
    },
    [agentId, addRequestCallback]
  );

  return {
    ...otherMephistoProps,
    makeRemoteCall,
    disconnectIssueText,
    _fullSocketProps,
  };
};

export {
  useMephistoRemoteQueryTask,
  ConnectionIndicator,
  MephistoContext,
  ErrorBoundary,
};
