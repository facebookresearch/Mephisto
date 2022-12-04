# annotator-tracker

This package provides `annotator-tracker` React hook which is used to log worker actions during their
working session.

A mephisto react project can import the hook so that it can track pre-defined actions or custom actions with returned
function from the hook.

The actions will be keep at browser's local storage and will be sent to mephisto server by using (`handleMetadataSubmit` of 
`useMephistoTask`) as a batch every 5000ms (default value - changeable).

**Default tracked actions**
- IP address
- Screen size
- Mouse click in window
- Mouse scroll
- Visibility change (ex: worker clicks out of browser or current tab)
- Focus in all elements
- Change in all `select` elements
- Click of all buttons
- Key input of all `input and textarea` elements
  - ```
    const specialKey = [0, 8, 13, 37, 38, 39, 40, 46]
    // click, enter, backspace, left, up, right, down, delete
    ``` 
- Blur on all `input (text) and textarea` elements
- Paste action
- Cut action
- Copy action

## Installation

Install from local folder (e.g. for local development):

```bash
cd packages/annotated/annotator-tracker
npm link

cd <app folder>
npm link annotator-tracker
```

## Usage (`useAnnotatorTracker`)

To integrate Mephisto with a front-end task interface, the easiest way is to use the provided React hook:

```jsx
import { useMephistoTask } from "mephisto-task";
import { useAnnotatorTracker } from "annotator-tracker";

function MyApp() {
    const {
        // ...
        handleMetadataSubmit,
        isLoading,
    } = useMephistoTask();
    
    logCustomAction = useAnnotatorTracker(handleMetadataSubmit, isLoading, 5000);
}
```

## Documentation

**Arguments:**

**`handleMetadataSubmit`**: The function to submit metadata returned from `useMephistoTask`.

**`isLoading`**: Boolean loading status of the screen to make sure only listen to existing elements.

**`logRate`**: Is the rate for sending data to server. The default value of this is 5000 milliseconds.

**Returns**
A function you can log a custom action.


### `logCustomAction`

`logCustomAction` receive two parameters are `type` and `action`:
- `type`: is a string to describe the type of action
- `action`: is an object to describe the action

**Example:**
```jsx
logCustomAction("screen_size", {
  screen_width: window.screen.width,
  screen_height: window.screen.height,
  window_width: window.innerWidth,
  window_height: window.innerHeight,
});