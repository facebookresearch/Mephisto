/* Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  getTaskConfig,
  requestAgent,
  isMobile,
  postCompleteTask,
  postCompleteOnboarding,
  getBlockedExplanation,
  postErrorLog,
  ErrorBoundary,
  postMetadata,
} from "./utils";

export * from "./MephistoContext";
export * from "./utils";
export * from "./live";
export * from "./RemoteTask.js";

/*
  The following global methods are to be specified in wrap_crowd_source.js
  They are sideloaded and exposed as global import during the build process:
*/
/* global
  getWorkerName, getAssignmentId, getAgentRegistration, handleSubmitToProvider
*/

const useMephistoTask = function () {
  const providerWorkerId = getWorkerName();
  const assignmentId = getAssignmentId();
  const isPreview = providerWorkerId === null || assignmentId === null;

  const reducerFn = (state, action) => ({
    ...state,
    ...action,
  });
  const initialState = {
    providerWorkerId: providerWorkerId,
    mephistoWorkerId: null,
    agentId: null,
    assignmentId: assignmentId,
    taskConfig: null,
    isPreview: isPreview,
    previewHtml: null,
    blockedReason: null,
    blockedExplanation: null,
    initialTaskData: null,
    isOnboarding: null,
    loaded: false,
  };

  const [state, setState] = React.useReducer(reducerFn, initialState);

  const handleSubmit = React.useCallback(
    (data) => {
      if (state.isOnboarding) {
        postCompleteOnboarding(state.agentId, data).then((packet) => {
          afterAgentRegistration(packet);
        });
      } else {
        postCompleteTask(state.agentId, data);
      }
    },
    [state.agentId]
  );
  const handleMetadataSubmit = React.useCallback(
    (...args) => {
      const metadata = {};
      // Update metadata
      for (const arg of args) {
        if (arg && arg.hasOwnProperty("type")) {
          const typeOfItemToAdd = arg["type"];
          metadata[typeOfItemToAdd] = arg;
        }
      }

      return new Promise(function (resolve, reject) {
        resolve(postMetadata(state.agentId, metadata));
      });
    },
    [state.agentId]
  );

  const handleFatalError = React.useCallback(
    (data) => {
      postErrorLog(state.agentId, data);
    },
    [state.agentId]
  );

  function handleIncomingTaskConfig(taskConfig) {
    if (taskConfig.block_mobile && isMobile()) {
      setState({ blockedReason: "no_mobile" });
    } else if (!state.isPreview) {
      requestAgent().then((data) => {
        console.log(data);
        afterAgentRegistration(data);
      });
    }
    setState({ taskConfig: taskConfig, loaded: isPreview });
  }
  function afterAgentRegistration(dataPacket) {
    const workerId = dataPacket.data.worker_id;
    const agentId = dataPacket.data.agent_id;
    const isOnboarding = agentId !== null && agentId.startsWith("onboarding");
    setState({ agentId: agentId, isOnboarding: isOnboarding });
    if (agentId === null) {
      setState({
        mephistoWorkerId: workerId,
        agentId: agentId,
        blockedReason: "null_agent_id",
        blockedExplanation: dataPacket.data.failure_reason,
      });
    } else {
      setState({
        mephistoWorkerId: workerId,
        mephistoAgentId: agentId,
        initialTaskData: dataPacket.data.init_task_data,
        loaded: true,
      });
    }
  }

  React.useEffect(() => {
    getTaskConfig().then((data) => handleIncomingTaskConfig(data));
  }, []);

  return {
    ...state,
    isLoading: !state.loaded,
    blockedExplanation:
      state.blockedExplanation ||
      (state.blockedReason && getBlockedExplanation(state.blockedReason)),
    handleSubmit,
    handleMetadataSubmit,
    handleFatalError,
  };
};

export { useMephistoTask, ErrorBoundary };
