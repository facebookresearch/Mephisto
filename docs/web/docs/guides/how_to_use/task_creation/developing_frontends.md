---
sidebar_position: 1
---

# Developing and debugging frontends

## The `mephisto-task` package

We provide the `mephisto-task` package for use in your front-end React tasks.

To install, add it to your npm project as such:

```
npm install mephisto-task
```

The `mephisto-task` project surfaces three React hooks depending on your use case:

1. `useMephistoTask` - Used for static tasks where one-time initial data is enough to power the task. See the example task in `/examples/static_react_task/` for an example project using this hook. 
2. `useMephistoLiveTask` - Used for multi-turn, socket-based tasks, such as a dialogue task. See the example task in `/examples/parlai_chat_task_demo/` for an example project using this hook.
3. `useMephistoRemoteProcedureTask` - Used for static tasks that require access to some remote function on the back-end, for example invoking a back-end model for model-assisted annotation. See the example task in `/examples/remote_procedure/mnist/` for an example project using this hook.

Complete documentation for each of the hooks can be found in the [associated README for the `mephisto-task` package](https://github.com/facebookresearch/Mephisto/tree/main/packages/mephisto-task).

## Reusable UI component libraries

#### `@annotated` [BETA]

To make common annotation tasks easier, we provide the `@annotated/*` suite of packages.

These suite of packages were formerly published under the `annotation-toolkit` and have now been broken down into their own individual packages. We provide helper UI components such as `@annotated/bbox`, `@annotated/video-player`, etc.

 We welcome contributions to these packages. To create your own package, you can clone the template folder at `packages/annotated/__template__`.

#### `bootstrap-chat`

For chat-based components, we provide custom UI components in the `bootstrap-chat` package. You can find further information for them in the [associated README for the `bootstrap-chat` package](https://github.com/facebookresearch/Mephisto/tree/main/packages/bootstrap-chat).

## Adding tips/feedback to tasks

To allow for greater communication between workers to workers and it is recommended to use the Tips component. 

### How to add Tips:
1. Add the Tips component to your task's react webapp code
2. Workers submit tips related to the task that they are working on.
3. **Once the task is shut down**, the researcher can review the submitted tips to either accept/reject them
4. The accepted tips are displayed by the Tips component when the task is launched again.

### Tips Code Snippet:
```jsx
  import { Tips } from "mephisto-worker-addons";

  return(
    <div>
      <SomeTaskCodeGoesHere />
      <Tips />
    </div>
  )
```

To learn more about the props in the Tips component you can check out its [readme](https://github.com/facebookresearch/Mephisto/blob/main/packages/mephisto-worker-addons/README.md#documentation).

How the component looks like: 

![](/tips_component.png)

### Reviewing the worker submitted tips
To review and accept/reject tips run `mephisto scripts local_db review_tips` in the terminal and follow the prompts.

Example output:
```bash
╔════════════════════════════════════════════════════════════════════════════════════════════╗
║                                             Tips Review                                    ║
╚════════════════════════════════════════════════════════════════════════════════════════════╝


                                              Task Names:                                              

 • react-static-task-with-tips                                                                         


Enter the name of the task that you want to review the tips of: react-static-task-with-tips 

                                              Tip 1 of 2                                               
╭────────────────────────┬───────────────────────────────────────────────────────────────────╮
│ Property               │ Value                                                             │
├────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ Tip Id                 │ a1a2f011-a7e9-465a-a8e0-9c079b081075                              │
├────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ Tip Header             │ 🎉 This is my first tip                                           │
├────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ Tip Text               │ This is my tip body                                               │
╰────────────────────────┴───────────────────────────────────────────────────────────────────╯

Do you want to (a)ccept, (r)eject, or (s)kip this tip? (Default: s) [a/r/s]: a

Tip Accepted

How much would you like to bonus the tip submitter? (Default: 0.0): 5

What reason would you like to give the worker for this tip? NOTE: This will be shared with 
the worker.(Default: Thank you for submitting a tip!): 

Bonus Successfully Paid!

                                              Tip 2 of 2                                               
╭────────────────────────┬────────────────────────────────────────────────────────────────────╮
│ Property               │ Value                                                              │
├────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Tip Id                 │ 8c33b8a3-5e7f-4156-8509-8b7b0fd2a347                               │
├────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Tip Header             │ Directions                                                         │
├────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ Tip Text               │ Make sure to follow the directions!                                │
╰────────────────────────┴────────────────────────────────────────────────────────────────────╯

Do you want to (a)ccept, (r)eject, or (s)kip this tip? (Default: s) [a/r/s]: r

Tip Rejected

There are no more tips to review
```

If you want to remove a tip that you accepted, then you can run `mephisto scripts local_db remove_tip` in the terminal and follow the prompts.

### How to add Feedback:
1. Add the Feedback component to your task's react webapp code and define questions.
2. Workers submit feedback related to the feedback questions.
3. **Once the task is shut down**, the researcher can review the feedback for the task.

### Feedback Code Snippet:
```jsx
  import { Feedback } from "mephisto-worker-addons";

  return(
    <div>
      <SomeTaskCodeGoesHere />
      <Feedback  
        questions={[
          "What is your favorite part of this task?",
          "Were you satisfied with this task?",
        ]}
      />
    </div>
  )
```
To learn more about the props in the Feedback component you can check out its [readme](https://github.com/facebookresearch/Mephisto/blob/main/packages/mephisto-worker-addons/README.md#documentation-1).

Image of feedback component:

![](/feedback_component.png)

### Reviewing the feedback
To review feedback run `mephisto scripts local_db review_feedback` in the terminal and follow the prompts.

Example output:
```bash
╔═════════════════════════════════════════════════════════════════════════════════════════════╗
║                                       Feedback Review                                       ║
╚═════════════════════════════════════════════════════════════════════════════════════════════╝


                                          Task Names:                                          

 • react-static-task-with-tips                                                                 


Enter the name of the task that you want to review the tips of: react-static-task-with-tips


                                           Questions                                           

 0 Were you satisfied with this task?                                                          
 1 What is your favorite part of this task?                                                    

If you want to filter feedback by a question, then enter the question number to filter on.
If you want to see feedback to all questions, enter "-1" (Default: -1) [-1/0/1]: -1
Do you want to filter out toxic comments? (Default: n) [y/n]: n
Do you want to see (r)eviewed or (u)nreviewed feedback? (Default: u) [r/u]: u

                            Unreviewed Feedback 1 of 2 From Agent 4                            
╭──────────────────┬──────────────────────────────────────────────────────────────────────────╮
│ Property         │ Value                                                                    │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Id               │ ee1679af-308c-4705-bb22-054b1406e043                                     │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Question         │ What is your favorite part of this task?                                 │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Text             │ The green button is vibrant!                                             │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Toxicity         │ 0.0012170307                                                             │
╰──────────────────┴──────────────────────────────────────────────────────────────────────────╯

Do you want to mark this feedback as reviewed? (Default: y) [y/n]: y

Marked the feedback as reviewed!

                            Unreviewed Feedback 2 of 2 From Agent 4                            
╭──────────────────┬──────────────────────────────────────────────────────────────────────────╮
│ Property         │ Value                                                                    │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Id               │ 373a1776-9ef4-4b4a-aba2-f2829ce3cd21                                     │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Question         │ Were you satisfied with this task?                                       │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Text             │ Yeah, it was easy and simple to complete.                                │
├──────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Toxicity         │ 0.0006023369                                                             │
╰──────────────────┴──────────────────────────────────────────────────────────────────────────╯

Do you want to mark this feedback as reviewed? (Default: y) [y/n]: n

Did not mark the feedback as reviewed!

You went through all the unreviewed feedback!

```

## Adding UI error handling to tasks

Currently, we have beta functionality for error handling. We provide a few ways of getting a signal into how your tasks are faring:

1. Auto-logging errors for React-based tasks
2. Proactively alerting crowd workers when an error occurs and encouraging them to contact you if this happens
3. Exposing error logging infrastructure for more advanced custom front-end use cases

### Automatic frontend logging
For #1 above, auto-logging can be enabled for React apps by importing the `<ErrorBoundary />` component and wiring it up as such:

```jsx
import { ErrorBoundary } from "mephisto-task";
...
const { handleFatalError, /* ... */ } = useMephistoTask();
...
return (
  <ErrorBoundary handleError={handleFatalError}>
    <MyApp />
  </ErrorBoundary>
);
```
This will automatically send an error packet to the backend Mephisto server when an error occurs.

### Alerting crowd-workers of issues
To opt into #2 above, you need to define a global variable as such:
```js
window._MEPHISTO_CONFIG_ = {
    /* required: */
    ADD_ERROR_HANDLING: true,
    /* optional: */
    ERROR_REPORT_TO_EMAIL: "example@example.org"
}
```

This will show a prompt as such if an uncaught error is detected:

![](/faq_ui_error_message.png)

### Advanced Usage
`handleFatalError` can also be used in any custom logic code you wish - for example, in handling errors for AJAX requests which live outside of the scope of React Error Boundaries:

```jsx
fetch("example.org/api/endpoint")
    .catch(err => handleFatalError(err.toString()));
```