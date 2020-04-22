/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from 'react';
import ReactDOM from 'react-dom';
import {
  TaskDescription,
  BaseFrontend,
} from './components/core_components.jsx';
import 'fetch';
import $ from 'jquery';

// setCustomComponents(UseCustomComponents);

/* global
  getWorkerName, getAssignmentId, getWorkerRegistrationInfo,
  getAgentRegistration, handleSubmitToProvider
*/

/* ================= Utility functions ================= */

// Determine if the browser is a mobile phone
function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
}

// Sends a request to get the task_config
function getTaskConfig() {
  return $.ajax({
    url: '/task_config.json',
    timeout: 3000, // in milliseconds
  });
}

function postData(url = '', data = {}) {
  // Default options are marked with *
  return fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
}

function postProviderRequest(endpoint, data) {
  var url = new URL(window.location.origin + endpoint);
  return postData(url, {provider_data: data})
    .then(res => res.json());
}

function requestAgent(mephisto_worker_id) {
  return postProviderRequest('/request_agent', getAgentRegistration(mephisto_worker_id));
}

function registerWorker() {
  return postProviderRequest('/register_worker', getWorkerRegistrationInfo());
}

// Sends a request to get the initial task data
function getInitTaskData(mephisto_worker_id, agent_id) {
  return postProviderRequest(
    '/initial_task_data',
    {'mephisto_worker_id': mephisto_worker_id, 'agent_id': agent_id},
  );
}

function postCompleteTask(agent_id, complete_data) {
  return postData('/submit_task', {'USED_AGENT_ID': agent_id, 'final_data': complete_data})
    .then(res => res.json())
    .then(function(data) {
      console.log('Submitted'); 
    });
}


/* ================= Application Components ================= */

class StaticApp extends React.Component {
  constructor(props) {
    super(props);
    
    this.state = {
      task_data: null,
    };
  }

  handleIncomingTaskData(task_data) {
    console.log('Got task data', task_data);
    this.setState({task_data: task_data});
  }

  componentDidMount() {
    getInitTaskData(this.props.mephisto_worker_id, this.props.agent_id)
      .then(packet => this.handleIncomingTaskData(packet.data.init_data));
  }

  handleSubmit(data) {
    postCompleteTask(this.props.agent_id, data).then(
      _data => handleSubmitToProvider(data)
    );
  }

  render() {
    if (this.state.task_data === null) {
      return <h1>Loading...</h1>
    }
    return <BaseFrontend 
      task_config={this.props.task_config} 
      onSubmit={(data) => {this.handleSubmit(data)}}
      task_data={this.state.task_data}
    />;
  }
}

class WorkerBlockedView  extends React.Component {
  render() {
    if (this.props.blocked_reason == 'no_mobile') {
      return <div>
          <h1>
            Sorry, this task cannot be completed on mobile devices.
            Please use a computer.
          </h1>
        </div>;
    } else if (this.props.blocked_reason == 'no_websockets') {
      return <div>
          <h1>
            Sorry, your browser does not support the required version
            of websockets for this task. Please upgrade to a modern browser.
          </h1>
        </div>;
    } else if (this.props.blocked_reason == 'null_agent_id') {
      return <div>
          <h1>
            Sorry, you have already worked on the maximum number of 
            these tasks available to you
          </h1>
        </div>;
    } else if (this.props.blocked_reason == 'null_worker_id') {
      return <div>
          <h1>
            Sorry, you are not eligible to work on any available tasks.
          </h1>
        </div>;
    }
    return <div> {this.props.blocked_reason} </div> ;
  }
}

class MainApp extends React.Component {
  constructor(props) {
    super(props);

    let provider_worker_id = getWorkerName();
    let assignment_id = getAssignmentId();
    let is_preview = true;
    if (provider_worker_id !== null && assignment_id !== null) {
      is_preview = false;
    } 

    let blocked_reason = null;

    this.state = {
      provider_worker_id: provider_worker_id,
      mephisto_worker_id: null,
      agent_id: null,
      assignment_id: assignment_id,
      task_config: null,
      is_preview: is_preview,
      preview_html: null,
      blocked_reason: blocked_reason,
    };
  }

  afterAgentRegistration(agent_data_packet) {
    console.log(agent_data_packet);
    let agent_id = agent_data_packet.data.agent_id;
    this.setState({agent_id: agent_id});
    if (agent_id == null) {
      console.log('agent_id returned was null')
      this.setState({blocked_reason: 'null_agent_id'});
    }
  }

  afterWorkerRegistration(worker_data_packet) {
    let mephisto_worker_id = worker_data_packet.data.worker_id;
    this.setState({mephisto_worker_id: mephisto_worker_id});
    if (mephisto_worker_id !== null) {
      requestAgent(mephisto_worker_id).then(data => this.afterAgentRegistration(data));
    } else {
      // TODO handle banned/blocked worker ids
      this.setState({blocked_reason: 'null_worker_id'});
      console.log('worker_id returned was null')
    }
  }

  handleIncomingTaskConfig(task_config) {
    let provider_worker_id = this.state.provider_worker_id;
    let assignment_id = this.state.assignment_id;
    if (task_config.block_mobile && isMobile()) {
      this.setState({blocked_reason: "no_mobile"})
    } else if (assignment_id != null && provider_worker_id != null) {
      registerWorker().then(data => this.afterWorkerRegistration(data));
    } 
    this.setState({task_config: task_config});
  }

  componentDidMount() {
    getTaskConfig().then(data => this.handleIncomingTaskConfig(data));
  }

  render() {
    if (this.state.blocked_reason !== null) {
      return <WorkerBlockedView 
        task_config={this.state.task_config} 
        blocked_reason={this.state.blocked_reason} 
      />;
    } else if (this.state.is_preview) {
      if (this.state.task_config === null) {
        return <div>Loading...</div>;
      } else {
        return <TaskDescription 
          task_config={this.state.task_config} 
          is_cover_page={true}
        />;
      }
    } else if (this.state.agent_id === null) {
      return <div>Loading...</div>;
    } else {
      return <StaticApp 
        task_config={this.state.task_config} 
        agent_id={this.state.agent_id} 
        mephisto_worker_id={this.state.mephisto_worker_id}
      />;
    }
  }
} 

ReactDOM.render(<MainApp />, document.getElementById('app'));
