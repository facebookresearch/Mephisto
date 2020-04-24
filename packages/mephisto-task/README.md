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

## Usage

In your component, you can call `useMephistoTask`:

```jsx
import { useMephistoTask } from "mephisto-task";

function MyApp() {
    const {
        taskConfig,
        providerWorkerId,
        mephistoWorkerId,
        agentId,
        assignmentId,

        taskData,
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

### `taskData`

The initial data to populate your task with. The crowdworker will use this data to perform their action.

### `handleSubmit`

A callback provided for the webapp to call to finalize and submit the resulting crowdworker's work back to the Mephisto system.

### `isPreview`

Essentially a proxy for `providerWorkerId === null && assignmentId === null`.

A boolean flag to be used to render a preview view for workers, e.g. on mTurk.

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