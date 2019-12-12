/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from 'react';
import ReactDOM from 'react-dom';
import Bowser from 'bowser';
import {Button} from 'react-bootstrap';

/* global
  getWorkerId, getAssignmentId, getWorkerRegistrationInfo,
  getAgentRegistration, handleSubmitToProvider
*/

/* ================= Utility functions ================= */

// Determine if the browser is a mobile phone
function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
}

function clickDone(worker_id, assignment_id, task_data) {
  // At the moment this function simply calls the submit method,
  // will later also have to talk to the server and maybe do validation
  // TODO validate entry
  // TODO talk to the server
  handleSubmitToProvider(worker_id, assignment_id, task_data);
}

// Sends a request to get the initial task data
function getInitTaskData(worker_id, assignment_id, callback_function) {
  var url = new URL(window.location.origin + '/initial_task_data')
  var params = {'worker_id': worker_id, 'assignment_id': assignment_id};
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
  fetch(url)
    .then(res => res.json())
    .then(function(data) {
    if (callback_function) {
      callback_function(data);
    }
  });
}

/* ================= Application Components ================= */

class MainApp extends React.Component {
  constructor(props) {
    super(props);

    let worker_id = getWorkerId();
    let assignment_id = getAssignmentId();
    let render_html = "<h1>Display Preview Here</h1>";
    if (worker_id !== null && assignment_id !== null) {
      render_html =  "<h1>Loading...</h1>";
    }

    this.state = {
      base_html: null,
      render_html: render_html,
      worker_id: worker_id,
      assignment_id: assignment_id,
      task_data: null,
    };

    this.raw_html_elem = null;
  }

  handleIncomingTaskData(data) {
    let base_html = data['html'];
    let fin_html = base_html;
    delete data['html'];
    let task_data = data;

    for (let [key, value] of Object.entries(task_data)) {
      let find_string = "${" + key + "}";
      fin_html = fin_html.replace(find_string, value);
    }

    this.setState({
      base_html: base_html,
      render_html: fin_html,
      task_data: task_data,
    });
  }

  componentDidMount() {
    let worker_id = this.state.worker_id;
    let assignment_id = this.state.assignment_id;
    if (assignment_id != null && worker_id != null) {
      getInitTaskData(worker_id, assignment_id, data => this.handleIncomingTaskData(data));
    }
  }

  render() {
    let worker_id = this.state.worker_id;
    let assignment_id = this.state.assignment_id;
    let task_data = this.state.task_data;
    let dangerous_html = <div
      ref={elem => {this.raw_html_elem = elem}}
      dangerouslySetInnerHTML={{__html: this.state.render_html}}
    />;
    return (
      <div>
        {dangerous_html}
        <Button onClick={() => clickDone(worker_id, assignment_id, task_data)}>
          <span
            style={{ marginRight: 5 }}
            className="glyphicon glyphicon-ok"
          />
          Submit
        </Button>
      </div>
    );
  }

  handleUpdatingRemainingScripts(curr_counter, scripts_left) {
    if (scripts_left.length == 0) {
      return;
    }
    let curr_script_name = "POST_LOADED_SCRIPT_" + curr_counter;
    let script_to_load = scripts_left.shift()
    if (script_to_load.text == '') {
      var head= document.getElementsByTagName('head')[0];
      var script= document.createElement('script');
      script.onload = () => {
        this.handleUpdatingRemainingScripts(curr_counter+1, scripts_left)
      };
      script.async = 1;
      script.src = script_to_load.src;
      head.appendChild(script);
    } else {
      const script_text = script_to_load.text;
      // This magic lets us evaluate a script from the global context
      (1, eval)(script_text);
      this.handleUpdatingRemainingScripts(curr_counter+1, scripts_left);
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // When the inner html has changed, we need to execute scripts!
    if (this.state.render_html != prevState.render_html) {
      let children = this.raw_html_elem.children;
      let scripts_to_load = [];
      for (let child of children) {
        let post_load_script_count = 0
        if (child.tagName == "SCRIPT") {
          scripts_to_load.push(child);
        }
      }
      if (scripts_to_load.length > 0) {
        this.handleUpdatingRemainingScripts(0, scripts_to_load);
      }
    }
  }
}

ReactDOM.render(<MainApp />, document.getElementById('app'));
