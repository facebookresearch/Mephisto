/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Bowser from "bowser";
const axios = require("axios");

/*
  The following global methods are to be specified in wrap_crowd_source.js
  They are sideloaded and exposed as global import during the build process:
*/
/* global
  getWorkerName, getAssignmentId, getWorkerRegistrationInfo,
  getAgentRegistration, handleSubmitToProvider, getProviderURLParams
*/

/* ================= Utility functions ================= */

const axiosInstance = axios.create();
export { axiosInstance };

function resolveProviderURLParams() {
  try {
    if (getProviderURLParams) {
      if (typeof getProviderURLParams === "function") {
        return getProviderURLParams();
      } else return getProviderURLParams;
    } else return null;
  } catch (e) {
    if (e instanceof ReferenceError) {
      // if getProviderURLParams isn't defined in wrap_crowd_source.js
      // just return nothing
      return null;
    } else {
      // some other error occured, probably when executing the code in
      // getProviderURLParams if it was a function. bubble the error up
      throw e;
    }
  }
}

axiosInstance.interceptors.request.use((config) => {
  const additionalParams = resolveProviderURLParams();
  if (!additionalParams) return config;

  // merge params
  config.params = { ...config.params, ...additionalParams };
  return config;
});

export function postData(url = "", data = {}) {
  // Default options are marked with *
  return axiosInstance({
    url: url,
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    headers: {
      "Content-Type": "application/json",
    },
    data: data, // body data type must match "Content-Type" header
  }).then((res) => res.data);
}

// Determine if the browser is a mobile phone
export function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
}

// Check if the current browser support WebSockets. using *bowser*
const browser = Bowser.getParser(window.navigator.userAgent);
export function doesSupportWebsockets() {
  return browser.satisfies({
    "internet explorer": ">=10",
    chrome: ">=16",
    firefox: ">=11",
    opera: ">=12.1",
    safari: ">=7",
    "android browser": ">=3",
  });
}

// Sends a request to get the task_config
export function getTaskConfig() {
  return axiosInstance("/task_config.json").then((res) => res.data);
}

export function postProviderRequest(endpoint, data) {
  var url = new URL(window.location.origin + endpoint).toString();
  return postData(url, { provider_data: data });
}

export function requestAgent(mephisto_worker_id) {
  return postProviderRequest(
    "/request_agent",
    getAgentRegistration(mephisto_worker_id)
  );
}

export function registerWorker() {
  return postProviderRequest("/register_worker", getWorkerRegistrationInfo());
}

// Sends a request to get the initial task data
export function getInitTaskData(mephisto_worker_id, agent_id) {
  return postProviderRequest("/initial_task_data", {
    mephisto_worker_id: mephisto_worker_id,
    agent_id: agent_id,
  });
}

export function postCompleteOnboarding(agent_id, onboarding_data) {
  return postProviderRequest("/submit_onboarding", {
    USED_AGENT_ID: agent_id,
    onboarding_data: onboarding_data,
  });
}

export function postCompleteTask(agent_id, complete_data) {
  return postData("/submit_task", {
    USED_AGENT_ID: agent_id,
    final_data: complete_data,
  })
    .then((data) => {
      handleSubmitToProvider(complete_data);
      return data;
    })
    .then(function (data) {
      console.log("Submitted");
    });
}

export function postErrorLog(agent_id, complete_data) {
  return postData("/log_error", {
    USED_AGENT_ID: agent_id,
    final_data: complete_data,
  })
    .then(function (data) {
      console.log("Error log sent to server");
    });
}

export function getBlockedExplanation(reason) {
  const explanations = {
    no_mobile:
      "Sorry, this task cannot be completed on mobile devices. Please use a computer.",
    no_websockets:
      "Sorry, your browser does not support the required version of websockets for this task. Please upgrade to a modern browser.",
    null_agent_id:
      "Sorry, you have already worked on the maximum number of these tasks available to you, or are no longer eligible to work on this task.",
    null_worker_id:
      "Sorry, you are not eligible to work on any available tasks.",
  };

  if (reason in explanations) {
    return explanations[reason];
  } else {
    return `Sorry, you are not able to work on this task. (code: ${reason})`;
  }
}
