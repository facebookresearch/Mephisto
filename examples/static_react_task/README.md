# Simple Static React Task
This example script is to demonstrate how to launch a simple task using a frontend webapp built in React. The "static" nature of this task means that all of the content required for a worker to complete the task must be set before the task is launched, and must be able to be sent to the app upon initialization. The actual app you write can vary in complexity however you like so long as this constraint is met.

This specific example can be run with:
```console
python run_task.py
```
and can additionally be launched with an onboarding step by specifying an onboarding qualification:
```console
python run_task.py mephisto.blueprint.onboarding_qualification=test-react-static-qualification
```
or by specifying the config file that already has this set:
```console
python run_task.py conf=onboarding_example
```

## Implementation
### Configuration
This task is configured using [Hydra](https://hydra.cc/) - details about using hydra to configure tasks can be read here and in other examples. For more about being able to customize the configuration files, please refer to the [Hydra documentation](https://hydra.cc/docs/intro). Under our current setup, using Hydra means that you must be in the same directory as the python script for hydra to correctly pick up the config files.
#### Setting reasonable defaults
In this script, we set certain configuration variables by default in every run:
```python
defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": 'local'},
    {"mephisto/provider": 'mock'},
    {"conf": "example"},
]
```
These defaults are handed to Hydra in order to ensure that by default, we run a task locally with a mock provider (so we can demo). We also set `conf` to `example`, which means this script by default will also load in all of the configuration variables set in `conf/example.yaml`.

If your task has other variables that you think will almost always be set to particular values (say you always expect `mephisto.blueprint.units_per_assignment` to be `1`) that differ from Mephisto's default for those values (if such a default exists), you can include them by default by adding a config file with your defaults to `conf` and adding the string path to it here in the list, like `conf/base`. See the ParlAI Chat demo for an example of this.
#### Creating and using override files
You can create override configuration files, such as `example.yaml` vs `onboarding_example.yaml` in the `conf` directory. Having these files makes it really easy to set multiple values at once. You can only select one such configuration file per run, using the `conf=example` argument.
#### Overriding on the command line
You can also override configuration variables on the command line. Say you want to launch your server on port 4000 rather than 3000, you can use:
```console
python run_task.py mephisto.architect.port=4000
```
To be able to launch with a `HerokuArchitect` rather than the default `LocalArchitect`, you can use:
```console
python run_task.py mephisto/architect=heroku
```
### Providing task data
In this case, the provided app demonstrates being able to send task data forward to the frontend. See the `run_task.py` script. Here we have:
```python
shared_state = SharedStaticTaskState(
    static_task_data=[
        {"text": "This text is good text!"},
        {"text": "This text is bad text!"},
    ],
    validate_onboarding=onboarding_always_valid,
)
```
This block of code is preparing two tasks, each with a `"text"` field set. When the task run is launched with `operator.validate_and_run_config(cfg.mephisto, shared_state)`, this creates two tasks for workers to work on, one for each entry in the `static_task_data` array.

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

You can also pass an additional dict under the key `task_config` as a part of `SharedStaticTaskState` to populate the frontend's `taskConfig` with those values for every task in a run.

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
An onboarding step can be added to tasks, which will be shown the first time a worker encounters a task with the same `onboarding_qualification` set. For Static React Tasks, calling `handleSubmit` when `isOnboarding` is true will submit the onboarding. The object passed will be sent to the Mephisto backend, wherein the contents will be passed to the `validate_onboarding` method of the `SharedTaskState`. If that method returns `False`, the worker will be prevented from working on the real task, or any future tasks with the same `onboarding_qualification` set. This task has one such button in `webapp/src/components/core_components.jsx` that is only shown if `isOnboarding` is true, and always submits a successful onboarding. See the [README on Blueprints](https://github.com/facebookresearch/Mephisto/blob/main/mephisto/abstractions/blueprints/README.md) for more info on the `SharedTaskState`.

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

#### Local Development

For local development, you may want to have changes made to your React code reflect locally without having to restart the server each time. To enable this, update the Hydra config's `mephisto.blueprint.link_task_source` value to `true` (default is `false`).

After running `python run_task.py`, you can then run `npm run dev:watch` in the webapp folder to auto-regenerate the task_source file. Since the task source file is now symlinked, simply refreshing the browser will reflect your changes. You won't need to kill and restart the server each time anymore.

## Making your own static react task
In order to get started on your own task, it is a good idea to copy this `static_react_task` directory into your workspace and use it as a starting point. Generally you'll do the following:

1. Copy the `static_react_task` directory to your project directory
2. Update `static_task_data` in the `run_task.py` script to provide the required data for your task
3. Update any task-related variables in your `conf/my_new_config.yaml` file to make sense for your task.
4. Update `webapp/src/components/core_components.jsx` to have the frontend you'd like. Include an onboarding step if possible.
5. Run `run_task.py` to pilot your task over localhost.
6. Repeat 4 & 5 until you're happy with your task.
7. Launch a small batch on a crowd provider to see how real workers handle your task.
8. Iterate more.
9. Collect some good data.
