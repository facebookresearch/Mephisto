# Mephisto Core
The contents of the core folder comprise controllers for launching and monitoring tasks. They amount to the level above the data model, that operates on components in the data model. Each has a high level responsibility, detailed below. This leads to a hierarchy of classes that try to leverage the lower levels, where at the highest level the `MephistoOperator` coordinates the other parts of the system to launch and manage tasks.

The goal is to make components of the Mephisto architecture reusable without needing to buy into the whole system. If someone wanted to override any of the subcomponents of Mephisto (`Architect`s, `TaskRunner`s, `CrowdProvider`s, etc.) the rest of the system should still function. It's also beneficial for writing contained tests and keeping code complexity down within each module.

## `LocalMephistoDB`
An implementation of the Mephisto Data Model outlined in `MephistoDB`. This database stores all of the information locally via SQLite. Some helper functions are included to make the implementation cleaner by abstracting away SQLite error parsing and string formatting, however it's pretty straightforward from the requirements of MephistoDB.

## `Supervisor`
The supervisor is responsible for interfacing between human agents and the rest of the mephisto system. In short, it is the layer that abstracts humans and human work into `Worker`s and `Agent`s that take actions. To that end, it has to set up a socket to connect to the task server, poll status on any agents currently working on tasks, and process incoming agent actions over the socket to put them into the `Agent` so that a task can use the data. It also handles the initialization of an `Agent` from a `Worker`, which is the operation that occurs when a human connecting to the service is accepting a task.

At a high level, the supervisor manages establishing the abstraction by keeping track of `Job`s (a triple of `Architect`, `TaskRunner`, and `CrowdProvider`). The supervisor uses them for the following:
- The `Architect` tells the `Supervisor` where the server(s) that agents are communicating with is(/are) running. In `register_job`, a socket is opened for each of these servers.
- The `TaskRunner` contains details about the relevant task run, and is used for properly registering a new `Agent` the correct `Unit`. For this, in `_register_agent` it gets all `Unit`s that a worker is eligible for, reserves one, and then handles creating a new `Agent` out of the given `Worker`-`Unit` pair.
- The `CrowdProvider` is also used during the registration process. In the first part it ensures that upon a first connect by a new person, a corresponding `Worker` is created to keep records for that worker (`_register_worker`). Later it is used during `_register_agent` to ensure that the `Agent` class used is associated with the correct `CrowdProvider` and has its relevant abstractions.

From this point, all interactions are handled from the perspective of pure Mephisto `Agent`s, and the remaining responsibilities of the `Supervisor` are to ensure that, from the perspective of a `TaskRunner`, `Agent`s local python state is entirely representative of the actual state of the human worker in the task. In order to handle that it has three primary functions:
- Incoming messages from the server (which represent actions taken by human agents) are passed to the `pending_actions` queue of the `Agent` that corresponds with that human agent. Future calls to `Agent.act()` will pop off from this queue.
- Calls to `Agent.observe()` will add messages to that `Agent`'s `pending_observations` list. The `Supervisor` should periodically send messages from all `Agent`s through to the server, such that the person is able to recieve the operation.
- The `Supervisor` should also be querying for `Agent`'s state and putting any updates into the `Agent` itself, thus allowing tasks to know if an `Agent` has disconnected, returned a task, etc.

## `TaskLauncher`
The `TaskLauncher` class is a fairly lightweight class responsible for handling the process of launching units. A `TaskLauncher` is created for a specific `TaskRun`, and provided with `assignment_data` for that full task run. It creates `Assignment`s and `Unit`s for the `TaskRun`, and packages the expected data into the `Assignment`.  When a task is ready to go live, one calls `launch_units(url)` with the `url` that the task should be pointed to. If units need to be expired (such as during a shutdown), `expire_units` handles this for all units created for the given `TaskRun`.

(TODO) `TaskLauncher`s should parse the `TaskRun`'s `TaskConfig` to know what parameters to set. This info should be used to initialize the assignments and the units as specified. At the moment it initializes with some MOCK data.
(TODO) `TaskLauncher` will eventually be the gatekeeper for the old `max_connections` feature of MTurk, which only lets out units gradually as they are completed. This functionality needs to be restored here somehow. Right now it launches all the units at once.

## `MephistoOperator`
The `MephistoOperator` will be the highest level class in the Mephisto architecture, and it's responsible for starting up tasks, coordinating requests, and managing various little setup components for the Mephisto experience that will be detailed here when the class is actually written.

## Utils
The `utils.py` file contains a number of helper utils that (at the moment) rely on the local-storage implementation of Mephisto. These utils help navigate the files present in the mephisto architecture, identify task files, link classes, etc. Docstrings in this class explain in more detail.
