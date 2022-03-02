# bootstrap-chat

A set of UI components based on [Bootstrap v3](https://react-bootstrap-v3.netlify.app/components/alerts/) for facilitating chat-based tasks for Mephisto.

## Installation

```bash
npm install --save bootstrap-chat mephisto-task

# Note that `mephisto-task` is a peer-dependency of this library.
```

Install from local folder (e.g. for local development):

```bash
cd packages/bootstrap-chat
npm link

cd <app folder>
npm link bootstrap-chat

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html),
# you can also do the following to ensure that both the app
# and bootstrap-chat are using the same version of React:
# 
# cd packages/bootstrap-chat
# npm link ../<app folder>/node_modules/react

```

## Usage

This package contains both individual components for building a chat UI, as well as precomposed components that can get you going quickly.

We generally recommend starting with the precomposed components, unless you have an advanced use-case. We provide escape-hatches for easy customization of common behaviors.

### Example 1: The pre-composed ChatApp component

The most simplest way to get going with 0 customizations is just the following:

```jsx
import { ChatApp } from "bootstrap-chat";

ReactDOM.render(<ChatApp />, document.getElementById("root"));
```

### Example 2: Modifying ChatApp

From here, you can easily opt into adding custom components and behaviors via render prop overrides.

Let's consider a contrived example where we would like every incoming chat message to appear suffixed with 5 exclamation marks.

```jsx

import { ChatApp, ChatMessage } from "bootstrap-chat";

function MyChatApp() {
    return (
        <ChatApp
            renderMessage={({ message }) => <ChatMessage message={message.text + "!!!!!"} />}
        />);
}

```

Here we replace the rendering of the chat message with the `renderMessage` prop. This is one of the provided optional render overrides, for the others see below.

Note that we also import the `<ChatMessage />` component to use as part of the render method. We don't have to do this portion, and could easily just create our own isolated implementation, e.g. something like `<div>{message.text + "!!!!!"}</div>`. However this example illustrates how we can opt out of default behavior, while still having available to us primitives and core components that can get us back some of that functionality at our discretion. In this case, we'll still have the look and feel of the original chat message component, however with a custom message property.


## The `<ChatApp />` component

The `ChatApp` component exposes the following props: 

*Note: All render-based props will receive as part of their args both `mephistoContext` and `appContext`, which will be described in a separate section below.*


### `renderMessage({ message, idx, mephistoContext, appContext })`
A render prop that if implemented, overides the way a chat message is rendered.

**Arguments:**

**`message`**: An object with the following schema, this comes from the ParlAI framework:

```
{
    'id', // the speaker id for the message
    'update_id', // a unique id for the current message, gotten from the liveUpdate it came from
    'text', // the actual message text, the message should not be displayed if this value is undefined or an empty string
    'task_data', // any additional data payload, also used to update the `taskContext`
}
```

**`idx`**: The 0-based index of the current message in the list of all messages


### `renderSidePane({ mephistoContext, appContext })`
A render prop that if implemented, overrides the way the side pane is rendered.

### `renderTextResponse({ onMessageSend, inputMode, active, mephistoContext, appContext })`
A render prop that if implemented, overrides the way the response text box is rendered. The default implementation of `ChatApp` is rendering the `<TextResponse />` component here.

Note: If `renderResponse()` is also implemented, this render prop will be ignored.

This render prop is for cases where you'd like to minimally alter the response text box, while still keeping the default UI states for things like handling disconnects, inactivity, and the done state. For larger customizations and more control, we recommend implementing `renderReponse()` instead.

**Arguments:**

**`onMessageSend`**: A callback provided for you to invoke in your implementation. Invoking this callback will send the passed in message back to the server. Example usage: `onMessageSend({ text: textValue, task_data: {} })`

**`inputMode`**: Represents an enumeration for the status of the chat task. It is set to one of the following:

- `WAITING`: The current agent is ready but is waiting for a response from the server, e.g. waiting for an incoming chat message.
- `INACTIVE`: Occurs when something goes wrong, usually if the agent experiences a disconnect, timeout, the task is returned, or has expired.
- `DONE`: The task is complete.
- `READY_FOR_INPUT`: The current agent is ready and is ready to send over data.

**`active`**: A helper boolean, essentially is true when `inputMode` is `INPUT_MODE.READY_FOR_INPUT`


### `renderResponse({ onMessageSend, inputMode, mephistoContext, appContext })`
A render prop that if implemented, overrides the way the entire response panel is rendered. You will be responsible for handling all aspects of the panel in this case, such as determining what to show when an agent disconnects, the task enters an inactive state, and when the task is completed.

Note: If this render prop is implemented, `renderTextResponse()` will be ignored.

**Arguments:**
The arguments for this render prop are the same as for `renderTextResponse`, with the exception of the `active` helper prop. You can reference those above.


### `onMessagesChange(messages)`

A callback that will get called any time a new message is received. The callback will receive as an argument all messages received thus far.

### `defaultAppSettings`

This optional prop lets you provide some initial app settings for the `ChatApp`, setting some default values for `appContext.appSettings`.

### The `mephistoContext` argument

All render props will receive the `mephistoContext` argument.

This object is basically the return value of calling the `useMephistoLiveTask` hooks. Further documentation on these properties can be found in the [documentation for the `mephisto-task` package](https://github.com/facebookresearch/Mephisto/blob/main/packages/mephisto-task/README.md) under the `useMephistoLiveTask` section.

### The `appContext` argument

All render props will receive the `appContext` argument. This context is generally used to handle app-specific information, as opposed to Mephisto-specific information.

By the default, the `appContext` object contains the following properties:

**Arguments:**

**`taskContext`**: An object that reflects the current context of the app by merging in the `task_data` property of each subsequent chat message received. As expected, later messages will overwrite the context set by previous messages if a conflict in a property of `task_data` occurs.

**`appSettings`**: You can use this to have access to various app-wide settings. For example, the default implementation uses it for volume control - that is the sole property. `console.log(appContext.appSettings.volume)`

**`setAppSettings`**: This method can be used to set app-wide settings which the rest of the app will then have access to through `appContext.appSettings`. For example, `setAppSettings({ volume: 1 }) `. `setAppSettings` will automatically merge in the passed in object with the existing `appSettings` object, so you do not have to do this merge yourself. That is, you can only pass the values you'd like to change as the argument, and the other previous values will be kept intact.

**`onTaskComplete`**: A callback provided for you to invoke to finally submit the task.

