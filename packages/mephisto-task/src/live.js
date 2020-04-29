import { useMephistoTask } from "./index";

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

/* ================= Agent State Constants ================= */

// TODO move to shared file
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

const useMephistoLiveTask = function (config) {
  const hookProps = useMephistoTask();
  const liveProps = {
    agentStatus: null,
    agentState: null,
    postData: () => {},
    serverStatus: {},
  };

  // TODO: at some point be sure to call config.onNewData()

  return { ...hookProps, ...liveProps };
};

export { useMephistoLiveTask };
