# mephisto-task

This package provides two hooks to faciliate React-based front-end development for Mephisto tasks.

Use `useMephistoTask` for simple, static tasks or `useMephistoLiveTask` for multi-turn, socket-based tasks.

## Installation

```bash
npm install mephisto-task
```

Install from local folder (e.g. for local development):

```bash
cd packages/mephisto-task
npm link

cd <app folder>
npm link mephisto-task

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html), you can also do the following to ensure that both the app and mephisto-task are using the same version of React:
# 
# cd packages/mephisto-task
# npm link ../<app folder>/node_modules/react
```

## Usage (`useMephistoTask`)

```jsx
import { useMephistoTask } from "mephisto-task";

function MyApp() {
    const {
        taskConfig,
        agentId,
        assignmentId,

        initialTaskData,
        handleSubmit,
        isPreview,
        previewHtml,
        isOnboarding,
        blockedReason,

        // advanced usage:
        providerWorkerId,
        mephistoWorkerId,

    } = useMephistoTask();
}
```

## Documentation

The `useMephisoTask` React hook exposes the following fields:

### `taskConfig`
An arbitrary task-specific config object passed from the backend.

Example:
```json
{
    "block_mobile": true,
    "frame_height": 650,
    "get_task_feedback": false,
    "num_subtasks": 2,
    "question": "Who would you prefer to talk to for a long conversation?",
    "task_description": "Pick the AI that you find more engaging."
}
```
### `agentId`

An `agentId `is another way of representing a worker working on a task. A single task might have multiple `agentId`s, for example in the case of conversational chat tasks. An agent could also be a model-in-the-loop instead of a worker. Usually you'll want to use `agentId` in your task code to represent workers. 

### `assignmentId`

When a worker accepts a task, an `assignmentId` is created to represent the pairing between the worker and the task.

### `initialTaskData`

The initial data to populate your task with. The worker will use this data to perform their action.

### `handleSubmit(payload)`

A callback provided for the webapp to finalize and submit the worker's resulting work back to Mephisto.

### `isPreview`

Essentially a convenient proxy for `assignmentId === null && providerWorkerId === null`.

A boolean flag to be used to render a preview view for workers, e.g. on mTurk.

See `previewHtml` as well, which uses this flag to provide a helper prop for describing static preview screens.

### `isLoading`

A boolean flag to be used to render a loading state while a task is handshaking with the Mephisto server backend and initializing. Once the `initialTaskData` is loaded, this will be set to `true`.

### `previewHtml`

A preview HTML snippet to show for the task in preview mode. You can use this to provide a static task preview screen or use `isPreview` for something more custom.

### `isOnboarding`

A flag to determine if the current task data is from a real task or an onboarding task. Allows rendering different views for onboarding. Submission is still handled with `handleSubmit`.

### `blockedReason`

A string-based code that when not null means that the current user is blocked from working on the current task.

A sentence description for the `blockedReason` can be looked up with the helper function `getBlockedExplanation()` as such:

```jsx
import { getBlockedExplanation } from "mephisto-task";

// Normally you would get blockedReason from useMephistoTask instead of setting it, but just showing here for illustrative purposes
const blockedReason = 'no_mobile':

getBlockedExplanation(blockedReason)
// returns -> "Sorry, this task cannot be completed on mobile devices. Please use a computer.

```

### `providerWorkerId` (advanced usage)

The ID created for the worker by the provider, e.g. mTurk.

### `mephistoWorkerId` (advanced usage)

The ID created for the worker by Mephisto.


---

## Usage (`useMephistoLiveTask`)

```jsx
import { useMephistoLiveTask } from "mephisto-task";

function MyApp() {
    const {
        // This hook includes ALL of the props
        // specified above with useMephistoTask,
        // while also including the following:
        connect,
        destroy,
        sendMessage

        agentState,
        agentStatus,

        connectionStatus,
    } = useMephistoLiveTask(
        onConnectionStatusChange: (connectionStatus) => {
            
        },
        onStateUpdate: ({state, status}) => {

        },
        onMessageReceived: (message) => {

        },
        config, // optional overrides for connection constants
        customConnectionHook, // (advanced usage) optional - provide your own hook for managing the under-the-hood connection mechanism to communicate with the Mephisto server. The default (useMephistoSocket) uses websockets.
    );
}
```

### `connect(agentId)`

Starts a persistent socket connection between the current `agentId` and the Mephisto live server.

### `destroy()`

Closes the socket connection that was created with the Mephisto live server. This connection cannot be reopened. 

### `sendMessage(payload)`

Once a connection is established, sends a message over the socket connection to the Mephisto live server on behalf of the agent.

### `agentState`

This object may contain agent-specific information that the live server updates.

For example, in the case of a server disconnect, the `agentState` will update with:

```
{
    done_text: <message describing the disconnect>,
    task_done: true
}
```

### `agentStatus`

Can be one of:

`AGENT_STATUS.NONE` \
`AGENT_STATUS.ONBOARDING` \
`AGENT_STATUS.WAITING` \
`AGENT_STATUS.IN_TASK` \
`AGENT_STATUS.DONE`

`AGENT_STATUS.RETURNED` \
`AGENT_STATUS.TIMEOUT` \
`AGENT_STATUS.EXPIRED` \
`AGENT_STATUS.DISCONNECT` \
`AGENT_STATUS.PARTNER_DISCONNECT` \
`AGENT_STATUS.MEPHISTO_DISCONNECT`


### `connectionStatus` (advanced usage)

Can be one of:

`CONNECTION_STATUS.INITIALIZING` \
`CONNECTION_STATUS.CONNECTED`

`CONNECTION_STATUS.RECONNECTING_ROUTER` \
`CONNECTION_STATUS.RECONNECTING_SERVER` 

`CONNECTION_STATUS.FAILED` \
`CONNECTION_STATUS.WEBSOCKETS_FAILURE` \
`CONNECTION_STATUS.DISCONNECTED` \
`CONNECTION_STATUS.DISCONNECTED_ROUTER` \
`CONNECTION_STATUS.DISCONNECTED_SERVER`


### Override options with the `config` object

```js
{
    sendThreadRefresh /* = 100 */,    
    heartbeatTime /* = 6000 */,
    refreshSocketMissedResponses /* = 5 */,
    routerDeadTimeout /* = 10 */,
    connectionDeadMephistoPing /* = 20000 */
}
```