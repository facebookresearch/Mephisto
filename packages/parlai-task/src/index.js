import React from "react";
import { getTaskConfig, registerWorker, requestAgent, isMobile } from "./utils";

class ParlAITask extends React.Component {
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
    this.setState({ agent_id: agent_id });
    if (agent_id == null) {
      console.log("agent_id returned was null");
      this.setState({ blocked_reason: "null_agent_id" });
    }
  }

  afterWorkerRegistration(worker_data_packet) {
    let mephisto_worker_id = worker_data_packet.data.worker_id;
    this.setState({ mephisto_worker_id: mephisto_worker_id });
    if (mephisto_worker_id !== null) {
      requestAgent(mephisto_worker_id).then((data) =>
        this.afterAgentRegistration(data)
      );
    } else {
      // TODO handle banned/blocked worker ids
      this.setState({ blocked_reason: "null_worker_id" });
      console.log("worker_id returned was null");
    }
  }

  handleIncomingTaskConfig(task_config) {
    let provider_worker_id = this.state.provider_worker_id;
    let assignment_id = this.state.assignment_id;
    if (task_config.block_mobile && isMobile()) {
      this.setState({ blocked_reason: "no_mobile" });
    } else if (assignment_id != null && provider_worker_id != null) {
      registerWorker().then((data) => this.afterWorkerRegistration(data));
    }
    this.setState({ task_config: task_config });
  }

  componentDidMount() {
    getTaskConfig().then((data) => this.handleIncomingTaskConfig(data));
  }

  render() {
    return this.props.children({
      blocked_reason: this.state.blocked_reason,
      task_config: this.state.task_config,
      is_preview: this.state.is_preview,
      agent_id: this.state.agent_id,
      mephisto_worker_id: this.state.mephisto_worker_id,
    });
  }
}

export { ParlAITask };

function ChatMessage({ message, color }) {
  return (
    <div style={message_container_style}>
      <div style={message_style}>{message}</div>
    </div>
  );
}
