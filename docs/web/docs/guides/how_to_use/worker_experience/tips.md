---
sidebar_position: 2
---

# Adding Tips
To allow for greater communication between workers and workers and it is recommended to use the Tips component. 

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
