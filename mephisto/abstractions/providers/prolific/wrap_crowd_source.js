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
\------------------------------------------*/

// The following is the nanoevents npm library (https://github.com/ai/nanoevents/blob/main/index.js) manually processed as such:
// 1. transpiled to support more browser targets using the Babel transpiler (https://babeljs.io/repl#?browsers=defaults&build=&builtIns=false&corejs=false&spec=false&loose=false), and
// 2. minified using a JS minifier (https://www.toptal.com/developers/javascript-minifier)
var eventEmitter=function(){return{events:{},emit:function(f){for(var b=this.events[f]||[],c=arguments.length,e=new Array(c>1?c-1:0),a=1;a<c;a++)e[a-1]=arguments[a];for(var d=0,g=b.length;d<g;d++)b[d].apply(b,e)},on:function(b,c){var a,d=this;return(null===(a=this.events[b])|| void 0===a?void 0:a.push(c))||(this.events[b]=[c]),function(){var a;d.events[b]=null===(a=d.events[b])|| void 0===a?void 0:a.filter(function(a){return c!==a})}}}}


const PROVIDER_TYPE = 'prolific';
// As for back-end (see `mephisto.abstractions.providers.prolific.api.constants.StudyCodeType`)
const STUDY_CODE_TYPE_COMPLETED = 'COMPLETED';
// These URL params must be the same as were used in the URL that is used in
// `mephisto.abstractions.providers.prolific.prolific_utils._ec2_external_url`
const STUDY_URL_PARTICIPANT_ID_PARAM = 'participant_id';
const STUDY_URL_STUDY_ID_PARAM = 'study_id';
const STUDY_URL_SUBMISSION_ID_PARAM = 'submission_id';


// Prolific IMPLEMENTATION
function getWorkerName() {
  // Prolific worker name is passed via url params as STUDY_URL_PARTICIPANT_ID_PARAM
  // (Prolific Participant ID)
  let urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(STUDY_URL_PARTICIPANT_ID_PARAM);
}


function getAssignmentId() {
  // Prolific assignment ID is passed via url params as STUDY_URL_SUBMISSION_ID_PARAM
  // (Prolific Submission ID)
  let urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(STUDY_URL_SUBMISSION_ID_PARAM);
}


function getProlificStudyId() {
  let urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(STUDY_URL_STUDY_ID_PARAM);
}


function getAgentRegistration() {
  // Prolific agents are created using the Mephisto `worker_id` and Prolific `submission_id`
  return {
    worker_name: getWorkerName(),
    agent_registration_id: getAssignmentId() + "-" + getWorkerName(),
    prolific_study_id: getProlificStudyId(),
    assignment_id: getAssignmentId(),
    provider_type: PROVIDER_TYPE,
  };
}


function handleSubmitToProvider(task_data) {
  // Redirecting a worker to the Prolific Study page back.
  // Otherwise, this worker will stay at our project's page without ability to finish his job
  var completionCode = STUDY_CODE_TYPE_COMPLETED + '_' + getProlificStudyId();
  window.location.href='https://app.prolific.co/submissions/complete?cc=' + completionCode;
}

const events = eventEmitter();


window._MEPHISTO_CONFIG_ = window._MEPHISTO_CONFIG_ || {};
window._MEPHISTO_CONFIG_.EVENT_EMITTER = events;


window._MEPHISTO_CONFIG_.get = (property) => {
  if (!(property in window._MEPHISTO_CONFIG_))
    throw new Error(`${property} does not exist in window.MEPHISTO_CONFIG`);
  else return window._MEPHISTO_CONFIG_[property];
};


window._MEPHISTO_CONFIG_.set = (property, value) => {
  window._MEPHISTO_CONFIG_[property] = value;
  events.emit(property, value);
};


/* === UI error handling code ======= */
window._MEPHISTO_CONFIG_.AUTO_SUBMIT_ERRORS = false;
window._MEPHISTO_CONFIG_.ADD_ERROR_HANDLING = false;
window._MEPHISTO_CONFIG_.ERROR_REPORT_TO_EMAIL = null;


let numErrorsCaught = 0;
let numErrorsReported = 0;
let userDisabledErrorPrompts = false;


// Adding event listener instead of using window.onerror prevents the error to be caught twice
window.addEventListener("error", function (event) {
  if (event.error.hasBeenCaught === true) {
    return false;
  }

  event.error.hasBeenCaught = true;
  numErrorsCaught += 1;
  if (window._MEPHISTO_CONFIG_.ADD_ERROR_HANDLING && !userDisabledErrorPrompts) {
    const fullErrorMessage = `${event.error.message}\n\n${event.error.stack}`;

    if (
      confirm(
        "An error has been detected and may affect the function of this task. " +
        "Would you like to report the error?\n\nDetails: " +
        event.error.message
      )
    ) {
      numErrorsReported += 1;
      const errorEmail = window._MEPHISTO_CONFIG_.ERROR_REPORT_TO_EMAIL;
      if (errorEmail) {
        prompt(`Please copy & paste the following in an email to: ${errorEmail}`, fullErrorMessage);
      } else {
        prompt(
          `Please copy & paste the following in an email to the task owner:`,
          fullErrorMessage
        );
      }
    }

    if (numErrorsCaught > 1) {
      userDisabledErrorPrompts = confirm(
        "We noticed you have gotten more than one of these error alerts. " +
        "Would you like to hide these alerts going forward?"
      );
      console.log(userDisabledErrorPrompts);
    }
  } else {
    // should we do auto-submission of errors?
  }
});
/* ================================== */
