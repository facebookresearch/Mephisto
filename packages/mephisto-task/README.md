# mephisto-task

## Installation

```bash
# Currently unsupported until the package is published to npm:

npm install mephisto-task
```

Install from local folder:

```bash
cd packages/mephisto-task
npm link

cd <app folder>
npm link mephisto-task
```

## Usage (`useMephistoTask`)

In your component, you can call `useMephistoTask` for simple, static tasks or `useMephistoLiveTask` for multi-turn socket-based communications:

```jsx
import { useMephistoTask } from "mephisto-task";

function MyApp() {
    const {
        taskConfig,
        providerWorkerId,
        mephistoWorkerId,
        agentId,
        assignmentId,

        initialTaskData,
        handleSubmit,
        isPreview,
        previewHtml,
        blockedReason,
    } = useMephistoTask();
}
```

## Documentation

The `useMephisoTask` React hook exposes the following fields:

### `taskConfig`
A config object passed from the backend.

Example:
```json
{
    block_mobile: true
    frame_height: 650
    get_task_feedback: false
    num_subtasks: 2
    question: "Who would you prefer to talk to for a long conversation?"
    task_description: "Placeholder Task Description - Javascript failed to load"
}
```

### `providerWorkerId`
### `mephistoWorkerId`
### `agentId`
### `assignmentId`

### `initialTaskData`

The initial data to populate your task with. The crowdworker will use this data to perform their action.

### `handleSubmit`

A callback provided for the webapp to call to finalize and submit the resulting crowdworker's work back to the Mephisto system.

### `isPreview`

Essentially a proxy for `providerWorkerId === null && assignmentId === null`.

A boolean flag to be used to render a preview view for workers, e.g. on mTurk.

### `isLoading`


A boolean flag to be used to render a loading state while a task is handshaking with the server backend and initializing. Once the initialTaskData is loaded, this will be set to `true`.

### `previewHtml`

A preview HTML snippet to show for the task in preview mode.

### `blockedReason`

A code that when not null means that the current user is blocked from the current task.

A sentence description for the `blockedReason` can be looked up as such:

```jsx
import { getBlockedExplanation } from "mephisto-task";

// Normally you would get blockedReason from useMephistoTask instead of setting it, but just showing here for illustrative purposes
const blockedReason = 'no_mobile':

getBlockedExplanation(blockedReason)
// returns -> "Sorry, this task cannot be completed on mobile devices. Please use a computer.

```


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

        connectionStatus,
        agentState,
        agentStatus,
    } = useMephistoLiveTask(
        onConnectionStatusChange: (connectionStatus) => {
            
        },
        onStateUpdate: ({state, status}) => {

        },
        onMessageReceived: (message) => {

        },
        config // optional overrides
    );
}
```

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