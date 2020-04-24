import $ from "jquery";
import "fetch";

/*
  The following global methods are to be specified in wrap_crowd_source.js
  They are sideloaded and exposed as global import during the build process:
*/
/* global
  getWorkerName, getAssignmentId, getWorkerRegistrationInfo,
  getAgentRegistration, handleSubmitToProvider
*/

/* ================= Utility functions ================= */

export function postData(url = "", data = {}) {
  // Default options are marked with *
  return fetch(url, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data), // body data type must match "Content-Type" header
  });
}

// Determine if the browser is a mobile phone
export function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
}

// Sends a request to get the task_config
export function getTaskConfig() {
  return $.ajax({
    url: "/task_config.json",
    timeout: 3000, // in milliseconds
  });
}

export function postProviderRequest(endpoint, data) {
  var url = new URL(window.location.origin + endpoint);
  return postData(url, { provider_data: data }).then((res) => res.json());
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

export function postCompleteTask(agent_id, complete_data) {
  return postData("/submit_task", {
    USED_AGENT_ID: agent_id,
    final_data: complete_data,
  })
    .then((res) => res.json())
    .then((data) => {
      handleSubmitToProvider(complete_data);
      return data;
    })
    .then(function (data) {
      console.log("Submitted");
    });
}

export function getBlockedExplanation(reason) {
  const explanations = {
    no_mobile:
      "Sorry, this task cannot be completed on mobile devices. Please use a computer.",
    no_websockets:
      "Sorry, your browser does not support the required version of websockets for this task. Please upgrade to a modern browser.",
    null_agent_id:
      "Sorry, you have already worked on the maximum number of these tasks available to you",
    null_worker_id:
      "Sorry, you are not eligible to work on any available tasks.",
  };

  if (reason in explanations) {
    return explanations[reason];
  } else {
    return `Sorry, you are not able to work on this task. (code: ${reason})`;
  }
}
