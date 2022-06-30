# mephisto-worker-addons

The Tips component will allow task authors to set up a communication channel to solicit "tips" from workers to share with other workers, thus allowing for the "crowdsourcing" of the instructions for tasks as well. We find that workers sometimes will share these tips in third-party forums or via emails to the task authors. This feature creates a more vetted channel for such communication.

## Installation

```bash
npm install --save mephisto-worker-addons
```

Install from local folder (e.g. for local development):

```bash
cd packages/mephisto-worker-addons
npm link

cd <app folder>
npm link mephisto-worker-addons

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html),
# you can also do the following to ensure that both the app
# and mephisto-worker-addons are using the same version of React:
# 
# cd packages/mephisto-worker-addons
# npm link ../<app folder>/node_modules/react
```

## Usage (`Tips`)


```jsx
import { Tips } from "mephisto-worker-addons";

function App() {
  return (
    <div>
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

## Documentation
The Tips component accepts the following props.
### `list`
The `list` prop accepts an array of objects where each object has a header property and a text property. This property is where the initial data for the tips is defined.
### `disableUserSubmission`
The `disableUserSubmission` prop accepts a boolean where a true value hides the text inputs and hides the submit button. Setting `disableUserSubmission` to false keeps the user inputs and submit button visible. 
The default value of this prop is false.
### `handleSubmit`
The `handleSubmit` prop accepts a function that runs when the "Submit Tip" button is pressed instead of the default behavior of submitting a tip. The tipData property can be passed down through to the function. This method can only be ran when `disableUserSubmission` is set to false.
### `tipData`
The `tipData` parameter exists when using the `handleSubmit` property. It records the inputted header and body of the submitted tip. The parameter is an object of the type:
```
{
  header: "this is a tip header",
  text: "this is a tip body"
}
```
### `headless`
The `headless` prop accepts a boolean where a a true value removes most of the styling and a false value keeps the original styling. The default value of this prop is false.
### `maxHeight`
This prop accepts a string that specifies the maximum height for the tips popup. ex: maxHeight="30rem". Content that overflows can be navigated to using the scrollbar.
### `width`
This prop accepts a string that specifies the width for the tips popup. ex: width="25rem".
### `placement`
This prop accepts a string that specifies the placement of the tips popup relative to the "Show/Hide Tips" button. 

It accepts values of "top-start", "top", "top-end", "right-start", "right", "right-end", "bottom-start", "bottom", "bottom-end","left-start", "left", "left-end". 

Only some of these values will be able to be applied in certain cases. For example, if the button is in the top right corner of the screen, then only the bottom and right values will be recognized as the left and top values would lead to the popup overflowing. 

The default value for this prop is "top-start", but this may not always be applied as mentioned in the case above.
### `maxHeaderLength`
The max character length of a tip header before an error message is shown. The default value for this prop is 72.
### `maxTextLength`
The max character length of tip text before an error message is shown. The default value for this prop is 500.


## Usage(`Feedback`)
```jsx
import { Feedback } from "mephisto-worker-experience";

function App() {
  return (
    <div>
      <Feedback
        headless={false}
        handleSubmit={(text)=> console.log(text)}
      />
    </div>
  );
}
```

## Documentation
### `headless`
The `headless` prop accepts a boolean where a a true value removes most of the styling and a false value keeps the original styling. The default value of this prop is false.
### `handleSubmit`
The `handleSubmit` prop accepts a function that runs when the "Submit Feedback" button is pressed instead of the default behavior of submitting feedback. The text property can be passed down through to the function.
### `width`
The `width` prop accepts a string that sets the width and min-width of the textarea. ex: width="30rem" sets the textarea width and min-width to 30rem. The default value for this prop is 18rem.
### `maxTextLength`
The max character length of feedback text before an error message is shown. The default value for this prop is 700.
### `createTip(header, text)`
This method is meant to be used as a parameter to the `handleSubmitMetadata` function of the `mephisto-task` library. The `createTip(header, text)` takes two strings as parameters. If one or both of the parameters are not a string then an error gets thrown. If both the two parameters are strings then the following object gets returned:
```
{
  header: header,
  text: text,
  type: "tips"
}
```

### `createFeedback(text)`
This method is meant to be used as a parameter to the `handleSubmitMetadata` function of the `mephisto-task` library. The `createFeedback(text)` takes one string as parameters. If the parameter is not a string then an error gets thrown. If the parameter is a string then the following object gets returned:
```
{
  text: text,
  type: "feedback"
}
```


### General Info
When a tip is submitted, `handleMetadataSubmit(payload)` from the `mephisto-task` package is ran.


The payload accepts:
```js
{
    header: string,
    text: string,
    type: "tips"
}
```
or
```js
{
    text: string,
    type: "feedback"
}
```

