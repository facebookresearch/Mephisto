# Simple Static React Task
This example script is to demonstrate how to launch a simple task using a frontend webapp built in React. The "static" nature of this task means that all of the content required for a worker to complete the task must be set before the task is launched, and must be able to be sent to the app upon initialization. The actual app you write can vary in complexity however you like so long as this constraint is met.

This specific example can be run with:
```console
python examples/static_react_task/run_task.py
```
and can additionally be launched with an onboarding step using:
```console
python examples/static_react_task/run_task.py --use-onboarding true
```

## Implementation
### Configuration
This task is configured using the `MephistoRunScriptParser`, and more details about using this utility can be found viewing other examples, or by checking the documentation (TODO). This task adds an additional argument for `--use-onboarding` to demonstrate how to have an onboarding step before the main static react task.
### Providing task data
In this case, the provided app demonstrates being able to send task data forward to the fronted. See the `run_task.py` script. Here we have:
```python
extra_args = {
    "static_task_data": [
        {"text": "This text is good text!"},
        {"text": "This text is bad text!"},
    ]
}
```
This block of code is preparing two tasks, each with a `"text"` field set. When the task run is launched with `operator.parse_and_launch_run_wrapper(shlex.split(ARG_STRING), extra_args=extra_args)`, this creates two tasks for workers to work on, one for each entry in the array.

This data is later pulled via the `useMephistoTask` hook, and when a worker accepts a task, they will be given the contents of one of the entries as their `initialTaskData`. See the `webapp/src/app.jsx` file. We render
```js
<BaseFrontend
  taskData={initialTaskData}
  onSubmit={handleSubmit}
  isOnboarding={isOnboarding}
/>
```
which if you look at the `webapp/src/components/core_components.jsx` file you can see pulling `text` directly out of the `taskData` as it was set in `static_task_data`:
```js
<p className="title is-3 is-spaced">{taskData.text}</p>
```
This is the flow for providing data to a static react task.

#### Adding taskConfig

You can also pass an additional dict under the key `task_config` as a part of `extra_args` to populate the frontend's `taskConfig` with those values for every task in a run.

### Getting data back
From within the frontend, any call to the `handleSubmit` method will store the data in any object passed as an argument to the local filestorage:

```js
<button
  className="button is-success is-large"
  onClick={() => onSubmit({ rating: "good" })}
>
  Mark as Good
</button>
```

This data can later be viewed using `MephistoDataBrowser` or other scripts.

### Onboarding
An onboarding step can be added to tasks, which will be shown the first time a worker encounters a task with the same `--onboarding-qualification` set. For Static React Tasks, calling `handleSubmit` when `isOnboarding` is true will submit the onboarding. If the object passed has the flag `{"success": false}` in it, the worker will be prevented from working on the real task, or any future tasks with the same `--onboarding-qualification` set. This task has one such button in `webapp/src/components/core_components.jsx` that is only shown if `isOnboarding` is true, and always submits a successful onboarding.

```js
<button
  className="button is-link"
  onClick={() => onSubmit({ success: true })}
>
  Move to main task.
</button>
```

### Building the react app
In `run_task.py` we have a step for building the frontend before running anything: `build_task()`. This method in theory only needs to be called on the first run, or when changes are made to the `webapp` directory.

## Making your own static react task
In order to get started on your own task, it is a good idea to copy this `static_react_task` directory into your workspace and use it as a starting point. Generally you'll do the following:

1. Copy the `static_react_task` directory to your project directory
2. Update `static_task_data` in the `run_task.py` script to provide the required data for your task
3. Update the task-related `ARG_STRING` variables in `run_task.py` to make sense for your task.
4. Update `webapp/src/components/core_components.jsx` to have the frontend you'd like. Include an onboarding step if possible.
5. Run `run_task.py` to pilot your task over localhost.
6. Repeat 4 & 5 until you're happy with your task.
7. Launch a small batch on a crowd provider to see how real workers handle your task.
8. Iterate more.
9. Collect some good data.