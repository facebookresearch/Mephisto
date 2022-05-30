# mephisto-worker-experience

This package provides the Tips component to aid in the creation of user-interfaces for Mephisto

## Installation

```bash
npm install --save mephisto-worker-experience
```

Install from local folder (e.g. for local development):

```bash
cd packages/mephisto-worker-experience
npm link

cd <app folder>
npm link mephisto-worker-experience

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html),
# you can also do the following to ensure that both the app
# and mephisto-worker-experience are using the same version of React:
# 
# cd packages/mephisto-worker-experience
# npm link ../<app folder>/node_modules/react
```

## Usage (`Tips`)

```jsx
import { Tips } from "mephisto-worker-experience";

function App() {
  return (
    <div className="card">
      <h1>Here Are Some Tips:</h1>
      <Tips
        list={[
          {
            header: "Functional or Class Components?",
            text: "It is generally advised to use functional components as they are thought to be the future of React.",
          },
          {
            header: "When to Use Context?",
            text: "To avoid having to pass props down 3+ levels, the createContext() and useContext() methods can be used.  ",
          },
        ]}
      />
    </div>
  );
}

```
