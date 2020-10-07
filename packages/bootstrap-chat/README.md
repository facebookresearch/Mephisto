# bootstrap-chat

A Bootstrap-based set of UI components for facilitating chat-based tasks for Mephisto.

## Installation

```bash
npm install --save bootstrap-chat mephisto-task
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

Let's consider a contrived example where we would like every message to appear suffixed with 5 exclamation marks.

```jsx

import { ChatApp, ChatMessage } from "bootstrap-chat";

function MyChatApp() {
    return (
        <ChatApp
            renderMessage={({ message }) => <ChatMessage message={message.text + "!!!!!"} />}
        />);
}

```

Here we replace the rendering of the chat message with the `renderMessage` prop. However, note that we also import the `<ChatMessage />` component and use that as part of the rendering. We don't have to do this portion, and could easily just create our own isolated implementation. However this example illustrates how we can opt out of default behavior, while still having available to us primitives and core components that can get us back some of that default functionality at our discretion.


## `<ChatApp />` documentation

`ChatApp` exposes the following props: 

All render props will receive as part of their args both `mephistoContext` and `appContext`, which will be described below.


### `renderMessage({ message, idx, mephistoContext, appContext })`
A render prop that if implemented, overides the way a chat message is rendered.


```js
{
    message: {
        id,
        text,
        task_data
    },
    idx, // the 0-indexed position of this message with respect to all messages received

    mephistoContext, // the current MephistoContext
    appContext // the current AppContext
}
```

### `renderSidePane({ mephistoContext, appContext })`
A render prop that if implemented, overrides the way the side pane is rendered.

### `renderTextResponse({ onMessageSend, inputMode, active, mephistoContext, appContext })`
A render prop that if implemented, overrides the way the response text box is rendered. The default implementation of `ChatApp` is rendering a `<TextResponse />` component here.

Note: If `renderResponse()` is also implemented, this render prop will be ignored.

This render prop is for cases where you'd like to minimally alter the response text box. For larger customizations, we recommend implementing `renderReponse()` instead.

```js
{
    onMessageSend,
    inputMode,
    active, // helper boolean, essentially is true when inputMode is INPUT_MODE.READY_FOR_INPUT
}
```

### `renderResponse({ onMessageSend, inputMode, mephistoContext, appContext })`
A render prop that if implemented, overrides the way the entire response panel is rendered. You will be responsible for handling all aspects of the panel in this case.

Note: If this render prop is implemented, `renderTextResponse()` will be ignored.


### `onMessagesChange(messages)`

A callback that will get called any time a new message is received. The callback will receive as an argument all messages received thus far.