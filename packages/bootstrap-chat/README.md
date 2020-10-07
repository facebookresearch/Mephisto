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

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html), you can also do the following to ensure that both the app and bootstrap-chat are using the same version of React:
# 
# cd packages/bootstrap-chat
# npm link ../<app folder>/node_modules/react

```

## Usage