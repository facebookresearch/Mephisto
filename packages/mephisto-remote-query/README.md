# mephisto-remote-query

A wrapper around the `mephisto-task` live hook exposing a simple remote execution -> callback model. 

## Installation

```bash
npm install --save mephisto-remote-query mephisto-task

# Note that `mephisto-task` is a peer-dependency of this library.
```

Install from local folder (e.g. for local development):

```bash
cd packages/mephisto-remote-query
npm link

cd <app folder>
npm link mephisto-remote-query

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html),
# you can also do the following to ensure that both the app
# and mephisto-remote-query are using the same version of React:
# 
# cd packages/mephisto-remote-query
# npm link ../<app folder>/node_modules/react

```

## Usage

This package contains an ease-of-use wrapper around `useMephistoLiveTask` that abstracts away most of the "live" considerations, such that you can generally treat the frontend as just having access to backend queries. We also include a few components that may be useful for displaying connection status, or for determining when something has gone wrong.

You can see the `mephisto_remote_query` example in the examples folder for possible usage.


### `makeRemoteCall({ targetEvent, args, callback })`
The primary function for interacting with the backend. Returns the `requestId` for the made remote call.

**Arguments:**

**`targetEvent`**: The string name of an event registered with the backend RemoteQueryBlueprint.
**`args`**: A json-serializable argument object that will be passed to the event handler on the backend.
**`callback`**: an optional callback that any backend responses will be called with, including more than once if a function yeilds multiple results. The input format is:
- `requestId`: The string `requestId` that should match with the returned `requestId` from this call.
- `response`: The (json-serializable) object sent in response to this request from the backend
- `args`: The original input args for this call (for convenience)

### `disconnectIssueText`
If this string is not `undefined`, it's because something has gone wrong with the task and it is now in a state that can no longer be completed. Further details can be seen in the `STATUS_TO_TEXT_MAP` constant provided by `mephisto-task`
