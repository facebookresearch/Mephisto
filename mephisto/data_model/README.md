# Data Model
This folder contains classes that generally represent the lowest levels of abstraction in Mephisto, lying as closely to the actual data as possible.

## Philosophy
The mephisto data model consists of important classes to formalize some of the concepts that are required for interacting with tasks, crowdsourcing providers, workers, etc. These classes try to abstract away some of the underlying convenience of working with mephisto into a common location, and are designed both to be extended from (in the form of creating child classes for specialized cases, or for the purpose of testing) and behind (like eventually supporting a common database for organizational use). All of the classes are to be database-backed, in that creation of these objects should populate the database, and most content will be linked through there. In this way, the state is maintained by the database, and the objects are collections of convenience methods for interacting with the underlying data model.

Note: This abstraction is broken specifically in the case of `Agent`s that are currently in a task, as their running task world relies on the specific `Agent` instance that is currently being tracked and updated by the `WorkerPool`.

## Database-backed Base Classes
The following classes are the units of Mephisto, in that they keep track of what mephisto is doing, where things are stored, history of workers, etc. The rest of the system in general should only be utilizing these classes to make any operations, allowing them to be a strong abstraction layer.

### `Project`
High level project that many crowdsourcing tasks may be related to. Useful for budgeting and grouping tasks for a review perspective. They are primarily a bookkeeping tool. At the moment they are fairly under-implemented, but can certainly be extended.

### `Task`
The `Task` class is required to create a group of `TaskRun`s for the purpose of aggregation and bookkeeping. Much of what is present in the current `Task` implementation can be deprecated. Much of the functionality here for ensuring that a task has common arguments and correct components is now stored in the `Blueprint` concept.

Eventually the `Task` code can be deprecated and replaced with useful aggregation functionality across `TaskRun`s within.

### `TaskRun`
This class keeps track of the configuration options and all assignments associated with an individual launch of a task. It also provides utility functions for ensuring workers can be assigned units (`get_valid_units_for_worker`, `reserve_unit`).

Generally has 3 states:
- Setup (not yet launched, `_has_assignments=False`, `_is_completed=False`): Before launch while the Mephisto architecture is still building the components required to launch this run.
- In Flight (launched, `_has_assignments=True`, `_is_completed=False`): After launch, when tasks are still in flight and may still be updating statuses.
- Completed (all tasks done/expired, `_has_assignments=True`, `_is_completed=True`): Once a task run is fully complete and no tasks will be launched anymore, it's ready for review.

Configuration parameters for launching a specific run are stored in the form of a json dump of the configuration file provided for the launch.

### `Assignment`
This class represents a single unit of work, or a thing that needs to be done. This can be something like "annotate this specific image" or "Have a conversation between two specified characters." It can be seen as an individual instantiation of the more general `Task` described above. As it is mostly captured by the `Blueprint` running the task, the only remaining components are knowing where the data is stored (`get_assignment_data`), tracking the assignment status (`get_status`) and knowing which `Worker`s and `Unit`s are associated with that progress.

### `Unit`
This class represents the role that an individual fills in completing an assignment. An individual worker should only complete one `Unit` per assignment, which covers the idea of having multiple people in a conversation, or different annotators for a specific task. The `Unit` is the first abstract class that needs to be synced with a `CrowdProvider`, as in order to know the status of the work (generally if it's ongoing or disconnected or such), it may be necessary to talk to an external provider.

### `Worker`
This class represents an individual - namely a person. It maintains components of ongoing identity for a user. `Worker`s can be blocked, unblocked, and bonused. You can also get all of the `Agent`s associated with a worker. Ultimately, `Worker`s are tightly coupled with a `CrowdProvider`, as the identity of a person is tied to where we get them from.

### `Agent`
This class encompasses a worker as they are working on an individual assignment. It maintains details for the current task at hand such as start and end time, connection status, etc. Generally this is an abstraction the worker operating at a frontend and the backend interactions. The `WorkerPool` and `ClientIOHandler` classese are responsible for maintaining most of that abstraction, so this class mostly needs to implement ways to approve and reject work, as well as get a work's status or mark it as done when the final work is received.

### `Requester`
This class encompasses your identity as it is known by a `CrowdProvider` you intend to launch tasks on. It keeps track of some metadata on your account (such as your budget) but also some Mephisto usage statistics (such as amount spent in total from that requester).

### Qualification and GrantedQualification
These classes act as a method for assigning Mephisto-backed qualifications to workers in a manner such that the same qualifications can be used across multiple different crowd providers, or with crowd providers that don't normally provide a method for granting qualifications before a worker connects.

## Non-Database backed abstractions
Some classes in the data model aren't backed by the data model because they are generally lightweight views of existing data or transient containers.

### `Packet`
Encapsulates messages being sent from the `ClientIOhandler` to any Mephisto server.

## Constants
Some Mephisto constants that are able to standardize values across multiple classes live in the data model within the contants folder.
