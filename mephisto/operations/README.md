# Mephisto Operations
The contents of the operations folder comprise controllers for launching and monitoring tasks, as well as other classes that either operate on the data model or support the mid level of Mephisto's design. Each has a high level responsibility, detailed below. Within these classes there's something of a heirarchy depending on the amount of underlying infrastructure that a class is built upon. 

### High-level controller components
This level of components is reserved for modules that operate on the highest level of the Mephisto heirarchy. These should be either directly usable, or easy to bundle into scripts for the client/api.

- `Operator`: High-level class responsible for launching and monitoring a `TaskRun`. Generally initialized using a `RunScriptConfig` and the `validate_and_run_config` method.

At the moment only the `Operator` exists in this level, as the module that manages the process of launching and monitoring a complete data collection job. Modules on a similar level of complexity may be written for the review flow, and for packaging data for release.

### Mid-level connecting components
These components are responsible for tying some of the underlying data model components to the reality of what they represent. They ensure that tasks remain in sync with what is actually happening, such that the content on Mephisto matches what is present on crowd providers and architects, and to some degree to blueprints.

- `Supervisor`: Responsible for following the status of a worker from the point they attempt to accept a `Unit` until the `Unit` is either completed or returned. This includes spawning the threads that watch specific `Assignment`'s or `Unit`'s, evaluating onboarding and qualifications, and ensuring that reconnecting workers are directed to the correct agents. The supervisor acts as the bridge between `Architect`s and `Blueprints`.
- `registry.py`: Reponsible for keeping track of instances of all of the Mephisto core abstractions, such that the system is able to refer to them just by name. 
- `TaskLauncher`: Responsible for moving through an iterator or generator of assignments and units to be created, first creating the local Mephisto state to represent them and then later leveraging the `CrowdProvider` to launch them. Also ensures certain configuration invariants hold, such as a maximum number of concurrent tasks available.

### Low-level Mephisto infra
These modules contain functionality that is used to condense shared behavior from various parts of the Mephisto codebase into standard functionality and utilities.

- `config_handler.py`: Functions responsible for providing a consistent interface into a user's configuration file for Mephisto, stored at `~/.mephisto/config.yml`.
- `hydra_config.py`: Classes and functionality responsible for ensuring that Mephisto operates well using Hydra, including base classes to build Hydra structured configs from (such as the `RunScriptConfig`) and methods to simplify interacting with Hydra in the codebase.
- `logger_core.py`: Helpers to simplify the process of generating unique loggers and logging configuration for various parts of Mephisto. (Much still to be done here).
- `utils.py`: Various smaller utility functions that are used in many places within the Mephisto codebase. (Likely getting to a point where these should be grouped).


## `Operator`
The Operator is responsible for actually coordinating launching tasks. This is managed using the `validate_and_run_config` function. It takes in a Hydra `DictConfig` of arguments corresponding to the `Blueprint`, `Architect`, and `CrowdProvider` of choice. It can also take a `SharedTaskState` object to pass information that wouldn't normally be able to be parsed on the command line, or where it can only be extracted at runtime.

One important extra argument is `SharedTaskState.qualifications`, which allows configuring a task with requirements for workers to be eligibible to work on the task. Functionality for this can be seen in `data_model.qualifications`, with examples in how `operator` handles the `block_qualification`.

The lifecycle of an operator is to launch as many Jobs as desired using the `validate_and_run_config` function, and then to watch over their progress using the `wait_for_runs_then_shutdown` function. These methods cover the full requirements for launching and monitoring a job.

If `wait_for_runs_then_shutdown` is not used, it's always important to call the `shutdown` methods whenever an operator has been created. While tasks are underway, a user can use `get_running_task_runs` to see the status of things that are currently running. Once there are no running task runs, the `Operator` can be told to shut down.


## `Supervisor`
The supervisor is responsible for interfacing between human agents and the rest of the mephisto system. In short, it is the layer that abstracts humans and human work into `Worker`s and `Agent`s that take actions. To that end, it has to set up a socket to connect to the task server, poll status on any agents currently working on tasks, and process incoming agent actions over the socket to put them into the `Agent` so that a task can use the data. It also handles the initialization of an `Agent` from a `Worker`, which is the operation that occurs when a human connecting to the service is accepting a task.

At a high level, the supervisor manages establishing the abstraction by keeping track of `Job`s (a triple of `Architect`, `Blueprint`, and `CrowdProvider`). The supervisor uses them for the following:
- The `Architect` tells the `Supervisor` where the server(s) that agents are communicating with is(/are) running. In `register_job`, a socket is opened for each of these servers.
- The `Blueprint` contains details about the relevant task run, and is used for properly registering a new `Agent` the correct `Unit`. For this, in `_register_agent` it gets all `Unit`s that a worker is eligible for, reserves one, and then handles creating a new `Agent` out of the given `Worker`-`Unit` pair.
- The `CrowdProvider` is also used during the registration process. In the first part it ensures that upon a first connect by a new person, a corresponding `Worker` is created to keep records for that worker (`_register_worker`). Later it is used during `_register_agent` to ensure that the `Agent` class used is associated with the correct `CrowdProvider` and has its relevant abstractions.

From this point, all interactions are handled from the perspective of pure Mephisto `Agent`s, and the remaining responsibilities of the `Supervisor` are to ensure that, from the perspective of a `Blueprint`'s `TaskRunner`, the `Agent`s local python state is entirely representative of the actual state of the human worker in the task. In order to handle that it has three primary functions:
- Incoming messages from the server (which represent actions taken by human agents) are passed to the `pending_actions` queue of the `Agent` that corresponds with that human agent. Future calls to `Agent.act()` will pop off from this queue.
- Calls to `Agent.observe()` will add messages to that `Agent`'s `pending_observations` list. The `Supervisor` should periodically send messages from all `Agent`s through to the server, such that the person is able to recieve the operation.
- The `Supervisor` should also be querying for `Agent`'s state and putting any updates into the `Agent` itself, thus allowing tasks to know if an `Agent` has disconnected, returned a task, etc.

## `registry`
The `registry.py` file contains functions required for establishing a registry of abstraction modules for Mephisto to refer to. This allows Mephisto to properly re-initialize classes and get information for data stored in the MephistoDB without needing to store pickled modules, or information beyond the registration key.

The file exposes the `register_mephisto_abstraction` class decorator, which ensures that on import a specific module will be added to the given registry. The `fill_registries` function automatically populates the registry dicts with all of the relevant modules in Mephisto, though this should likely be expanded to allow users or repositories to mark or register their own Mephisto implementations.

Mephisto classes can then use the `get_<abstraction>_from_type` methods from the file to retrieve the specific modules to be initialized for the given abstraction type string.

## `TaskLauncher`
The `TaskLauncher` class is a fairly lightweight class responsible for handling the process of launching units. A `TaskLauncher` is created for a specific `TaskRun`, and provided with `assignment_data` for that full task run. It creates `Assignment`s and `Unit`s for the `TaskRun`, and packages the expected data into the `Assignment`.  When a task is ready to go live, one calls `launch_units(url)` with the `url` that the task should be pointed to. If units need to be expired (such as during a shutdown), `expire_units` handles this for all units created for the given `TaskRun`.

`TaskLauncher`s will parse the `TaskRun`'s `TaskConfig` to know what parameters to set. This info should be used to initialize the assignments and the units as specified. The `TaskLauncher` can also be used to limit the number of currently available tasks using the `max_num_concurrent_units` argument, which prevents too many tasks from running at the same time, potentially overrunning the `TaskRunner` that the `Blueprint` has provided.


## `config_handler.py`
The methods in this module standardize how Mephisto interacts with the user configurations options for the whole system. These are stored in `"~/.mephisto/config.yml"` at the moment. The structure of the config file is such that it subdivides values to store into sections containing keys. Those keys can contain any value, but writing and reading data is done by referring to the `section` and the `key` for the data being written or read.

The following methods are defined:
- `get_config`: loads all of the contents of the mephisto config file.
- `write_config`: Writes an entirely new config to file
- `init_config`: Tries to create an initial configuration file if none exists
- `add_config_arg`: Sets the value for just one configuration arg in the whole set.
- `get_config_arg`: Returns a specific argument value from a section of the config.

## `hydra_config.py`
The hydra config module contains a number of classes and methods to make interfacing with hydra a little more convenient for Mephisto and its users. It defines common structured config types, currently the `MephistoConfig` and the `RunScriptConfig`, for use in user code. It also defines methods for handling registering those structured configs under the expected names, which the `registry` relies on. Lastly, it provides the `register_script_config` method, which lets a user define a structured config for use in their scripts without needing to initialize a hydra `ConfigStore`.

## `logger_core.py`
This module contains helpers to simplify the process of generating unique loggers and logging configuration for various parts of Mephisto. At the moment this only outlines the basic logging style that Mephisto uses, though much is still to be done in order to set up logging throughout Mephisto, simplified controls for getting debug information across certain files, and user configuration of Mephisto logs.

## Utils
The `utils.py` file contains a number of helper utils that (at the moment) rely on the local-storage implementation of Mephisto. These utils help navigate the files present in the mephisto architecture, identify task files, link classes, etc. Docstrings in this class explain in more detail.