# Data Model
This folder contains classes that generally represent the lowest levels of abstraction in Mephisto, lying as closely to the actual data as possible.

## Philosophy
The mephisto data model consists of important classes to formalize some of the concepts that are required for interacting with tasks, crowdsourcing providers, workers, etc. These classes try to abstract away some of the underlying convenience of working with mephisto into a common location, and are designed both to be extended from (in the form of creating child classes for specialized cases, or for the purpose of testing) and behind (like eventually supporting a common database for organizational use). All of the classes are to be database-backed, in that creation of these objects should populate the database, and most content will be linked through there. In this way, the state is maintained by the database, and the objects are collections of convenience methods for interacting with the underlying data model.

Note: This abstraction is broken specifically in the case of `Agent`s that are currently in a task, as their running task world relies on the specific `Agent` instance that is currently being tracked and updated by the `Supervisor`.

## Database-backed Base Classes
The following classes are the units of Mephisto, in that they keep track of what mephisto is doing, where things are stored, history of workers, etc. The rest of the system in general should only be utilizing these classes to make any operations, allowing them to be a strong abstraction layer.

### `Project`
High level project that many crowdsourcing tasks may be related to. Useful for budgeting and grouping tasks for a review perspective. They are primarily a bookkeeping tool.

### `Task`
This class contains all of the required tidbits for launching a set of assignments, including where to find the frontend files to deploy (based on the `Blueprint`), possible arguments for configuring the assignments more exactly (a set of `TaskParam`s), the associated project (if supplied).

(TODO) at the moment, the required state creation for bookkeeping for a task (creating the directory to store assignment information and such) is handled in the `new` method for `Task`. This should really be hidden away behind the `MephistoDB` or `core.utils`. Much of the complexity for task creation is now hidden behind `task_type` (`Blueprint`s) though, so it's possible this needs to be totally removed.

### `TaskRun`
This class keeps track of the configuration options and all assignments associated with an individual launch of a task. It also provides utility functions for ensuring workers can be assigned units (`get_valid_units_for_worker`, `reserve_unit`).

Generally has 3 states:
- Setup (not yet launched, `_has_assignments=False`, `_is_completed=False`): Before launch while the Mephisto architecture is still building the components required to launch this run.
- In Flight (launched, `_has_assignments=True`, `_is_completed=False`): After launch, when tasks are still in flight and may still be updating statuses.
- Completed (all tasks done/expired, `_has_assignments=True`, `_is_completed=True`): Once a task run is fully complete and no tasks will be launched anymore, it's ready for review.

(TODO) Definitely needs a way to keep track of parameters.
(TODO) Responsible for determining worker eligibility? Perhaps this is better placed into the `Supervisor`? As of now there's an `is_eligible` function in `Worker` that should probably be assigned with this.

### `Assignment`
This class represents a single unit of work, or a thing that needs to be done. This can be something like "annotate this specific image" or "Have a conversation between two specified characters." It can be seen as an individual instantiation of the more general `Task` described above. As it is mostly captured by the `Blueprint` running the task, the only remaining components are knowing where the data is stored (`get_assignment_data`), tracking the assignment status (`get_status`) and knowing which `Worker`s and `Unit`s are associated with that progress.

### `Unit`
This class represents the role that an individual fills in completing an assignment. An individual worker should only complete one `Unit` per assignment, which covers the idea of having multiple people in a conversation, or different annotators for a specific task. The `Unit` is the first abstract class that needs to be synced with a `CrowdProvider`, as in order to know the status of the work (generally if it's ongoing or disconnected or such), it may be necessary to talk to an external provider.

### `Worker`
This class represents an individual - namely a person. It maintains components of ongoing identity for a user. `Worker`s can be blocked, unblocked, and bonused. You can also get all of the `Agent`s associated with a worker. Ultimately, `Worker`s are tightly coupled with a `CrowdProvider`, as the identity of a person is tied to where we get them from.

### `Agent`
This class encompasses a worker as they are working on an individual assignment. It maintains details for the current task at hand such as start and end time, connection status, etc. Generally this is an abstraction the worker operating at a frontend and the backend interactions. The `Supervisor` class is responsible for maintaining most of that abstraction, so this class mostly needs to implement ways to approve and reject work, as well as get a work's status or mark it as done when the final work is received.

(TODO) actually implement end time of an assignment, perhaps by leveraging `mark_done`?

### `Requester`
This class encompasses your identity as it is known by a `CrowdProvider` you intend to launch tasks on. It keeps track of some metadata on your account (such as your budget) but also some Mephisto usage statistics (such as amount spent in total from that requester).

## Mephisto Abstraction Interfaces
Specific implementations can be made to extend the Mephisto data model to work with new crowd providers, new task types, and new backend server architectures. These are summarized below, but other sections go more in-depth.

(TODO) link other READMEs here.

### `CrowdProvider`
A crowd provider is a wrapper around any of the required functionality that Mephisto will need to utilize to accept work from workers on a specific service. Ultimately it comprises of an extension of each of `Worker`, `Agent`, `Unit`, and `Requester`. More details can be found in the `providers` folder, where all of the existing `CrowdProvider`s live.

### `Blueprint`
A blueprint is the essential formula for running a task on Mephisto. It accepts some number of parameters and input data, and that should be sufficient content to be able to display a frontend to the crowdworker, process their responses, and then save them somewhere. It comprises of extensions of the `AgentState` (data storage), `TaskRunner` (actual steps to complete the task), and `TaskBuilder` (resources to display a frontend) classes. More details are provided in the `server/blueprints` folder, where all the existing `Blueprint`s live.

### `Architect`
An `Architect` is an abstraction that allows Mephisto to manage setup and maintenance of task servers for you. When launching a task, Mephisto uses an `Architect` to build required server files, launch that server, deploy the task files, and then later shut it down when the task is complete. More details are found in the `server/architects` folder, along with the existing `Architects`.

## Non-Database backed abstractions
Some classes in the data model aren't backed by the data model because they are generally lightweight views of existing data or transient containers.

### `Packet`
Encapsulates messages being sent from the `Supervisor` to any Mephisto server.

### `TaskConfig`
Keeps track of specific parameters that are necessary to launch a task on any crowd provider, like `title`, `description`, `tags`, `quantity`, `pay_amount`, etc. `TaskRuns` leverage the `TaskConfig` to know what they're doing.

(TODO) this should be deprecated or merged into whatever kind of arg parsing we're going to be using.

## Constants
Some Mephisto constants that are able to standardize values across multiple classes live in the data model

(TODO) Does it make sense to move these into a `constants`, folder, and have them be pure?

### `AssignmentState`
These track the possible valid assignment states that Mephisto is aware of
### Blueprint.AgentState
These track the possible states that an individual agent may be in
### `constants.py`
This file is the catch-all for any other shared constants when there aren't enough in a similar category to make its own file.
