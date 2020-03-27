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


function getWorkerName() {
    // MTurk worker name is passed via url params
    let urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('workerId');
}

function getAssignmentId() {
    // MTurk assignment id is passed via url params
    let urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('assignmentId');
}

function getHITId() {
    // MTurk assignment id is passed via url params
    let urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('hitId');
}

function getWorkerRegistrationInfo() {
    // MTurk workers are registered by name only
    return {
        worker_name: getWorkerName(),
        provider_type: 'mturk_sandbox',
    };
}

function getAgentRegistration(mephisto_worker_id) {
    // MTurk agents are created using the Mephisto worker_id
    // and the supplied assignment id
    return {
        worker_id: mephisto_worker_id,
        agent_registration_id: getAssignmentId(),
        assignment_id: getAssignmentId(),
        hit_id: getHITId(),
        provider_type: 'mturk_sandbox',
    };
}

function handleSubmitToProvider(task_data) {
    // MTurk agents need to submit some task parameters
    let urlParams = new URLSearchParams(window.location.search);
    task_data['assignmentId'] = getAssignmentId();
    task_data['workerId'] = getWorkerName();
    var form = document.createElement('form');
    document.body.appendChild(form);
    for (var name in task_data) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = task_data[name];
        form.appendChild(input);
    }
    form.method = 'POST';
    form.action = urlParams.get('turkSubmitTo') + '/mturk/externalSubmit';
    form.submit();
}
