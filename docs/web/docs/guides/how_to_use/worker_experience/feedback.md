---
sidebar_position: 3
---

# Adding Feedback
To allow for greater communication between workers and researchers it is recommended to use the Feedback component. 

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
