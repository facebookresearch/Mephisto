<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# mephisto-addons

The WorkerOpinion component will allow researchers to receive opinions about their Tasks or some ideas how to improve them.

## Installation

```bash
npm install --save mephisto-addons
```

Install from local folder (e.g. for local development):

```bash
cd packages/mephisto-addons
npm link

cd <app folder>
npm link mephisto-addons

# If you're getting an invalid hooks error (https://reactjs.org/warnings/invalid-hook-call-warning.html),
# you can also do the following to ensure that both the app
# and mephisto-addons are using the same version of React:
# 
# cd packages/mephisto-addons
# npm link ../<app folder>/node_modules/react
```

## Usage(`WorkerOpinion`)
```jsx
import { WorkerOpinion } from "mephisto-addons";

return(
  <div>
    <SomeTaskCodeGoesHere />
    
    <WorkerOpinion  
      questions={[
        "What is your favorite part of this task?",
        "Were you satisfied with this task?",
      ]}
    />
  </div>
)
```

## Documentation

### `headless`
The `headless` prop accepts a boolean where a true value removes most of the styling and a false value keeps the original styling. The default value of this prop is false.

### `questions`
The `questions` prop accepts a list of strings where each string is displayed with its own textarea input. When reviewing the Worker Opinion in the task, there is an option to filter by question. By default, there are no questions defined and Worker Opinion is collected under the 'General Worker Opinion' label.

### `handleSubmit`
The `handleSubmit` prop accepts a function that runs when the "Submit opinion" button is pressed instead of the default behavior of submitting Worker Opinion. The text property can be passed down through to the function.

### `textAreaWidth`
The `textAreaWidth` prop accepts a string that sets the width of the text-area. ex: textAreaWidth="30rem" sets the text-area width. The default value for this prop is 100%.

### `maxTextLength`
The max character length of Worker Opinion text before an error message is shown. The default value for this prop is 700.
