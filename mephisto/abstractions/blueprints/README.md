# Blueprints
## Overview
Blueprints serve to package tasks (and groups of similar tasks) into a reusable format. They can be used to work through piloting tasks, collecting data, testing different formats, etc. They're also used by the architecture to simplify the data accumulation and review processes. The `StaticBlueprint` is a good starting example of how to implement a blueprint.

## Implementation Details
### `AgentState`
The agent state is responsible for defining the data that is important to store for a specific `Unit`, as well as methods for writing that locally to disk. To abstract this, it must implement the following methods:
- `set_init_state(data)`: given data provided by the `get_init_data_for_agent` method, initialize this agent state to whatever starting state is relevant for this `Unit`.
- `get_init_state()`: Return the initial state to be sent to the agent for use in the frontend.
- `load_data()`: Load data that is saved to file to re-initialize the state for this `AgentState`. Generally data should be stored in `self.agent.get_data_dir()`, however any storage solution will work as long as it remains consistent.
- `get_data()`: Return the stored data for this task in the format containing everything the frontend needs to render and run the task.
- `get_parsed_data()`: Return the stored data for this task in the format that is relevant for review or packaging the data.
- `save_data()`: Save data to a file such that it can be re-initialized later. Generally data should be stored in `self.agent.get_data_dir()`, however any storage solution will work as long as it remains consistent, and `load_data()` will be able to find it.
- `update_data()`: Update the local state stored in this `AgentState` given the data sent from the frontend. Given your frontend is what packages data to send, this is entirely customizable by the task creator.

### `TaskBuilder`
`TaskBuilder`s exist to abstract away the portion of building a frontend to however one would want to, allowing Mephisto users to design tasks however they'd like. They also can take build options to customize what ends up built. They must implement the following:
- `build_in_dir(build_dir)`: Take any important source files and put them into the given build dir. This directory will be deployed to the frontend and will become the static target for completing the task.
- `get_extra_options()`: Return the specific task options that are relevant to customize the frontend when `build_in_dir` is called.

### `TaskRunner`
The `TaskRunner` component of a blueprint is responsible for actually stepping `Agent`s through the task when it is live. It is, in short, able to set up task control. A `TaskRunner` needs to implement the following:
- `get_init_data_for_agent`: Provide initial data for an assignment. If this agent is reconnecting (and as such attached to an existing task), update that task to point to the new agent (as the old agent object will no longer receive data from the frontend).
- `run_assignment`: Handle setup for any resources required to get this assignment running. It will be launched in a background thread, and should be tolerant to being interrupted by cleanup_assignment.
- `cleanup_assignment`: Send any signals to the required thread for the given assignment to tell it to terminate, then clean up any resources that were set within it.
- `get_data_for_assignment` (optional): Get the data that an assignment is going to use when run. By default, this pulls from `assignment.get_assignment_data()` however if a task has a special storage mechanism or data type, the assignment data can be fetched here. 

### `SharedTaskState`
A blueprint is able to create a container that handles any shared data that is initialized during a task or modified between tasks, or for function hooks that are used across a run. The following hooks are already provided in the base:
- `validate_onboarding`: A function that takes in an onboarding agent's `AgentState.get_data()` call, and should always return a boolean of if that state represents a successful onboarding completion.
- `worker_can_do_unit`: A function that takes in a `Worker` and a `Unit`, and should return a boolean representing if the worker is eligible to work on that particular unit.
- `on_unit_submitted`: A function that takes in a `Unit` after a `TaskRunner` ends, and is able to do any automatic post-processing operations on that unit that a Mephisto user may want.

## `Blueprint` Mixins
Blueprints sometimes share some component functionality that may be useful across a multitude of tasks. We capture these in mixins. Mephisto is able to recognize certain mixins in order to complete additional operations, however custom mixins may help cut down on boiler plate in common `run_task.py` scripts. As your tasks mature, we suggest utilizing blueprint mixins to share common workflows and design patterns you observe.
### `OnboardingRequired`
This mixin allows for blueprints that require people to complete an onboarding task _before_ they're even able to start on their first task. Usually this is useful for providing task context, and then quizzing workers to see if they understand what's provided. Tasks using this mixin will activate onboarding mode for new `Worker`s whenever the `mephisto.blueprint.onboarding_qualification` hydra argument is provided.
### `ScreenTaskRequired`
This mixin allows for blueprints that require people to complete a _test_ version of the real task the first time a worker does the task. This allows you to validate workers on a run of the real task, either on your actual data (when providing `SharedTaskState.screening_data_factory=False`) or on test data that you may more easily validate using (when providing a generator to `SharedTaskState.screening_data_factory`). The tasks should be the same as your standard task, just able to be easily validated. You **do pay** for screening tasks, and as such we ask you set `mephisto.blueprint.max_screening_units` to put a cap on how many screening units you want to launch.


## Implementations
### `StaticBlueprint`
The `StaticBlueprint` class allows a replication of the interface that MTurk provides, being able to take a snippet of `HTML` and a `.csv` file and deploy tasks that fill templates of the `HTML` with values from the `.csv`.

You can also specify the task data in a `.json` file, or by passing the data array or a generator to `SharedStaticTaskState.static_task_data`.

### `MockBlueprint`
The `MockBlueprint` exists to test other parts of the Mephisto architecture, and doesn't actually provide a real task.
