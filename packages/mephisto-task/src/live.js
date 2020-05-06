import React, { Children } from "react";
import { useMephistoTask, doesSupportWebsockets } from "./index";
import { useMephistoSocket } from "./socket_handler.jsx";

// REQUIRED STATE
// state = {
//   initialization_status: "initializing", // "initializing", "done", "failed", "browser_incompatible"
//   socket_status: null, // TODO improve this functionality for disconnects
//   agent_status: STATUS_WAITING, // TODO, start as STATUS_NONE when implementing onboarding
//   done_text: null,
//   task_done: false,
// }

// handleIncomingTaskData(taskData) {
//   console.log("Got task data", taskData);
//   let messages = taskData.raw_messages;
//   for (const message of messages) {
//     this.socket_handler.parseSocketMessage(message);
//   }
// }

// New implementation will take agent_status and agent_state.
// handleAgentStatusChange(agent_status, display_name, done_text) {
//   console.log("Handling state update", agent_status, this.state.agent_status);
//   if (agent_status != this.state.agent_status) {
//     // Handle required state changes on a case-by-case basis.
//     if ([STATUS_DONE, STATUS_PARTNER_DISCONNECT].includes(agent_status)) {
//       this.setState({ task_done: true, chat_state: "done" });
//       this.socket_handler.closeSocket();
//     } else if (
//       [
//         STATUS_DISCONNECT,
//         STATUS_RETURNED,
//         STATUS_EXPIRED,
//         STATUS_TIMEOUT,
//         STATUS_MEPHISTO_DISCONNECT,
//       ].includes(agent_status)
//     ) {
//       // ParlAI-specific logic
//       this.setState({ chat_state: "inactive", done_text: done_text });
//       this.socket_handler.closeSocket();
//     } else if (agent_status == STATUS_WAITING) {
//       this.setState({ messages: [], chat_state: "waiting" });
//     }
//     this.setState({ agent_status: agent_status, done_text: done_text });
//   }
//   if (display_name != this.state.agent_display_name) {
//     this.setState({ agent_display_name: display_name });
//   }
// }

// let socket_handler = null;
// socket_handler = (
//   <SocketHandler
//     onNewMessage={(new_message) => {
//       this.state.messages.push(new_message);
//       this.setState({ messages: this.state.messages });
//     }}
//     onNewTaskData={(new_task_data) =>
//       this.setState({
//         task_data: Object.assign(this.state.task_data, new_task_data),
//       })
//     }
//     onRequestMessage={() => this.setState({ chat_state: "text_input" })}
//     onForceDone={() => this.props.handleSubmit(this.state.messages)}
//     onSuccessfulSend={() =>
//       this.setState({
//         chat_state: "waiting",
//         messages: this.state.messages,
//       })
//     }
//     onAgentStatusChange={(agent_status, display_name, done_text) =>
//       this.handleAgentStatusChange(agent_status, display_name, done_text)
//     }
//     agent_display_name={this.state.agent_display_name}
//     onConfirmInit={() => this.setState({ initialization_status: "done" })}
//     onFailInit={() => this.setState({ initialization_status: "failed" })}
//     onStatusChange={(status) => this.setState({ socket_status: status })}
//     agent_id={this.props.agent_id}
//     initialization_status={this.state.initialization_status}
//     agent_status={this.state.agent_status}
//     messages={this.state.messages}
//     task_done={this.state.task_done}
//     ref={(m) => {
//       this.socket_handler = m;
//     }}
//     playNotifSound={() => this.playNotifSound()}
//   />
// );

// // Handle updates to state
// handleStateUpdate(update_packet) {
//   let agent_status = update_packet['agent_status'] || this.props.agent_status;
//   let agent_display_name = update_packet['agent_display_name'] || this.props.agent_display_name;
//   if (agent_status != this.props.agent_status || agent_display_name != this.props.agent_display_name) {
//     this.props.onAgentStatusChange(
//       agent_status,
//       agent_display_name,
//       update_packet['done_text'],
//     );
//   }
//   if (update_packet['is_final']) {
//     this.closeSocket();
//   }
// }

/* ================= Agent State Constants ================= */

const STATUS_NONE = "none";
const STATUS_ONBOARDING = "onboarding";
const STATUS_WAITING = "waiting";
const STATUS_IN_TASK = "in task";
const STATUS_DONE = "done";
const STATUS_DISCONNECT = "disconnect";
const STATUS_TIMEOUT = "timeout";
const STATUS_PARTNER_DISCONNECT = "partner disconnect";
const STATUS_EXPIRED = "expired";
const STATUS_RETURNED = "returned";
const STATUS_MEPHISTO_DISCONNECT = "mephisto disconnect";

const STATUS = {
  STATUS_NONE,
  STATUS_ONBOARDING,
  STATUS_WAITING,
  STATUS_IN_TASK,
  STATUS_DONE,
  STATUS_DISCONNECT,
  STATUS_TIMEOUT,
  STATUS_PARTNER_DISCONNECT,
  STATUS_EXPIRED,
  STATUS_RETURNED,
  STATUS_MEPHISTO_DISCONNECT,
};

const useMephistoLiveTask = function (props) {
  const [connectionStatus, setConnectionStatus] = React.useState("");
  const [agentState, setAgentState] = React.useState(null);
  const [agentStatus, setAgentStatus] = React.useState(null);

  const [messages, addMessage] = React.useReducer(
    (allMessages, newMessage) => [...allMessages, newMessage],
    []
  );

  const taskProps = useMephistoTask();
  const socketProps = useMephistoSocket({
    onStatusChange: (status) => {
      setConnectionStatus(status);
      props.onStatusChange(status);
    },
    onStateUpdate: ({ state, status }) => {
      setAgentState(state);
      setAgentStatus(status);
      props.onStateUpdate({ state, status });
    },
    onMessageReceived: (message) => {
      if (message.text === undefined) {
        message.text = "";
      }
      addMessage(message);
      props.onMessageReceived(message);
    },
  });

  if (!doesSupportWebsockets()) {
    taskProps.blockedReason = "no_websockets";
  }

  return {
    ...taskProps,
    ...socketProps,
    connectionStatus,
    agentState,
    agentStatus,
    messages,
  };
};

export { useMephistoLiveTask, useMephistoSocket, STATUS };
