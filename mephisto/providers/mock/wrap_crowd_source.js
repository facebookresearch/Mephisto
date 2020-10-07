/* Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


/* -------- wrap_crowd_source.js ---------\
This file comprises the functions required to interface between
a crowd provider's frontend and the crowd provider backend.

At a high level this involves getting the worker identifier and
assignment identifiers, and packaging any required information
for both to be able to register them with the backend database.

Returning None for the assignment_id means that the task is being
previewed by the given worker.
\------------------------------------------*/
auto_submit = false

// MOCK IMPLEMENTATION
function getWorkerName() {
    // Mock worker name is passed via url params
    urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('worker_id');
}

function getAssignmentId() {
    // mock assignment id is passed via url params
    urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('assignment_id');
}

function getWorkerRegistrationInfo() {
    // mock workers have no special registration
    return {
        worker_name: getWorkerName(),
        provider_type: 'mock',
    };
}

function getAgentRegistration(mephisto_worker_id) {
    // Mock agents are created using the Mephisto worker_id
    // and the supplied assignment id
    return {
        worker_id: mephisto_worker_id,
        agent_registration_id: getAssignmentId() + "-" + mephisto_worker_id,
        assignment_id: getAssignmentId(),
        provider_type: 'mock',
    };
}

function handleSubmitToProvider(task_data) {
    // Mock agents won't ever submit to a real provider
    alert("The task has been submitted! Data: " + JSON.stringify(task_data))
    return true;
}

// Adding event listener instead of using window.onerror prevents the error to be caught twice
window.addEventListener('error', function (event) {

    if (event.error.hasBeenCaught !== undefined){
    return false
  }
  event.error.hasBeenCaught = true
  if (!auto_submit) {
      if (confirm("Do you want to report the error?")) {
          prompt('send the following error to the email address: '+
          '[email address]', JSON.stringify(event.error.message))
            }
  }
  else {
    console.log("sending to email address: ####")
  }
  return true;
})
