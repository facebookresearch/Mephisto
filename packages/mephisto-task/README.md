# mephisto-task

This package provides two hooks to faciliate React-based front-end development for Mephisto tasks.

Use `useMephistoTask` for simple, static tasks, `useMephistoLiveTask` for multi-turn, socket-based tasks, and `useMephistoRemoteProcedureTask` for static tasks with access to backend queries (for model-in-the-loop tasks, for instance).

## Installation

```bash
npm install --save mephisto-task
```

Install from local folder (e.g. for local development):

```bash
cd packages/mephisto-task
npm link

cd <app folder>
npm link mephisto-task

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html),
# you can also do the following to ensure that both the app
# and mephisto-task are using the same version of React:
# 
# cd packages/mephisto-task
# npm link ../<app folder>/node_modules/react
```

## Usage (`useMephistoTask`)

To integrate Mephisto with a front-end task interface, the easiest way is to use the provided React hook:

```jsx
import { useMephistoTask } from "mephisto-task";

function MyApp() {
    const {
        taskConfig,
        agentId,
        assignmentId,
        initialTaskData,
        handleSubmit,
        handleMetadataSubmit,
        isLoading,
        isOnboarding,
        isPreview,
        previewHtml,
        blockedReason,

        // advanced usage:
        providerWorkerId,
        mephistoWorkerId,
    } = useMephistoTask();
}
```

## Documentation

The `useMephistoTask` React hook exposes the following fields:

### `taskConfig`
An arbitrary task-specific config object passed to the front-end from your back-end server. This `taskConfig` object can be specified from the `get_frontend_args` of the `Blueprint` Python class for your task.

Here is an example `taskConfig` that is specified in the [ParlAI Chat blueprint](`https://github.com/facebookresearch/Mephisto/blob/main/mephisto/server/blueprints/parlai_chat/parlai_chat_blueprint.py`):
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

An `agentId ` is the identifier that Mephisto uses to pair a worker with the specific task being worked on. Given this definition, a single worker will have a different `agentId` for each task that they work on.

A single task could have multiple `agentId`s, for example in the case of conversational chat tasks. 

Usually you'll want to use `agentId` to represent workers in your task code as opposed to `mephistoWorkerId` and `providerWorkerId` which are reserved for more advanced usages.

More details about Agents can be found in the [Mephisto architecture overview docs](https://github.com/facebookresearch/Mephisto/blob/main/docs/web/docs/explanations/architecture_overview.md#agent).

### `assignmentId`

An `assignmentId` uniquely represents the portion of the task that a worker will be working on.

More details about Assignments can be found in the [Mephisto architecture overview docs](https://github.com/facebookresearch/Mephisto/blob/main/docs/web/docs/explanations/architecture_overview.md#assignment).

### `initialTaskData`

This is the initial data that will be used to populate your task. The worker will use this data to perform their action.

For the static task blueprint, this can be specified via the `static_task_data` array argument for `SharedStaticTaskState`.

Generally speaking, the value is the `InitializationData` object that the `TaskRunner` returns in `get_data_for_assignment`, which comes from the set of `InitializationData` objects returned by the blueprint's `get_initialization_data` method.

### `handleSubmit(payload)`

A callback provided for the webapp to finalize and submit the worker's resulting work back to Mephisto.

### `handleMetadataSubmit(payload)`

A callback provided for the webapp to finalize and submit metadata to a Mephisto agent.

### `isLoading`

A boolean flag to be used to render a loading state while a task is handshaking with the Mephisto server backend and initializing. Once the `initialTaskData` is loaded, this will be set to `true`.

### `isOnboarding`

A flag to determine if the current task data is from a real task or an onboarding task. Allows rendering different views for onboarding. Submissions for onboarding tasks are still handled with `handleSubmit`.

### `isPreview`

Essentially a convenient proxy for `assignmentId === null && providerWorkerId === null`.

A boolean flag to be used to render a preview view for workers, e.g. on mTurk.

See `previewHtml` as well, which uses this flag to provide a helper prop for describing static preview screens.

### `previewHtml`

A preview HTML snippet to show for the task in preview mode. You can use this to provide a static task preview screen or use `isPreview` for something more custom.

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

For socket-based "live" tasks that require updates from a server (as opposed to static tasks), we provide a `useMephistoLiveTask` React hook.

```jsx
import { useMephistoLiveTask } from "mephisto-task";

function MyApp() {
    const {
        // This hook includes ALL of the props
        // specified above with useMephistoTask,
        // while also including the following:
        connect,
        destroy,
        sendLiveUpdate,

        agentStatus,

        connectionStatus,
    } = useMephistoLiveTask({
        onConnectionStatusChange: (connectionStatus) => {

        },
        onStatusUpdate: ({ status }) => {
            // Called when agentStatus updates
        }
        onLiveUpdate: (liveUpdate) => {

        },
        config, // optional overrides for connection constants
        customConnectionHook, // (advanced usage) optional - provide your own hook for managing the under-the-hood connection mechanism to communicate with the Mephisto server. The default (useMephistoSocket) uses websockets.
    });
}
```

### `connect(agentId)`

Starts a persistent socket connection between the current `agentId` and the Mephisto live server.

### `destroy()`

Closes the socket connection that was created with the Mephisto live server. This connection cannot be reopened. 

### `sendLiveUpdate(payload)`

Once a connection is established, sends an update packet over the socket connection to the Mephisto live server on behalf of the current agent.

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


### Override options with the `config` argument

In advanced cases, you may want to configure some of the socket behavior for live tasks. For these cases, `useMephistoLiveTask` accepts as an argument an optional `config` object that can be used to configure various socket polling constants.

These constants and their defaults are as follows:

```js
{
    sendThreadRefresh /* = 100 */,    
    heartbeatTime /* = 6000 */,
    refreshSocketMissedResponses /* = 5 */,
    routerDeadTimeout /* = 10 */,
    connectionDeadMephistoPing /* = 20000 */
}
```

For example, if you'd like to have the front-end poll the back-end less often (e.g. 1s as opposed to 100ms), you could configure this as such: `useMephistoLiveTask({ config: { sendThreadRefresh: 1000 } })`.

--- 

## Usage (`useMephistoRemoteProcedureTask`)

This hook is an ease-of-use wrapper around `useMephistoLiveTask` that abstracts away most of the "live" considerations, such that you can generally treat the frontend as just having access to backend queries. You can see the `mephisto_remote_procedure` example in the mephisto examples folder for possible usage.


### `remoteProcedure(targetEvent)`
The primary function for interacting with the backend. Returns a function that you can use to query for the specified `targetEvent`, either directly or with `invoke`.

**Arguments:**

**`targetEvent`**: The string name of an event registered with the backend RemoteProcedureBlueprint.

**Returns**
A function you can invoke in one of the following manners.

```js
// Using invoke
remoteProcedure("run_mnist_classifier") // create an RPC fn reference here
   .invoke({img: img_binary})
   .then(res => console.log(res))
   .catch(err => console.error(err))

// Creating a remote function to use inline with await syntax
const classifyNumber = remoteProcedure("run_mnist_classifier");
classifyNumber({img: img_binary})
    .then(res => updateClass(res));

// Using inline functions with await syntax (in async functions)
const result = await classifyNumber({img: img_binary});
```

The input arguments for `invoke` and for the returned function are the same, and both accept any json-serializable argument object that will be passed to the backend event handler.

The response in both cases is a promise, for which the return value from the backend will be passed to.


### `disconnectIssueText`
If this string is not `undefined`, it's because something has gone wrong with the task and it is now in a state that can no longer be completed. Further details can be seen in the `STATUS_TO_TEXT_MAP` constant provided by `mephisto-task`
