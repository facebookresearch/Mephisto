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
    <div>
      <h1>Here Are Some Tips:</h1>
      <Tips
        handleSubmit={()=> console.log("Submitted!")}
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

## Documentation
The Tips component accepts the following props.
### `list`
The `list` prop accepts an array of objects where each object has a header property and a text property. This property is where the data for the tips is defined.
### `disableUserSubmission`
The `disableUserSubmission` property accepts a boolean where a true value hides the text inputs and hides the submit button. Setting `disableUserSubmission` to false keeps the user inputs and submit button visible. 
### `handleSubmit`
The `handleSubmit` property accepts a function that runs when the "Submit Tip" button is pressed. This method can only be ran when `disableUserSubmission` is set to false.