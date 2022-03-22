# CrowdProviders
The providers directory is home to the existing providers for Mephisto. This file describes high level what crowd providers do, important details on existing providers, and how to create a new `CrowdProvider` for an existing crowdsourcing service.

## Implementation Details
`CrowdProvider`s in short exist to be an abstraction layer between Mephisto and wherever we're sourcing the crowdwork from. Using `CrowdProvider`s lets Mephisto launch the same tasks all over the place using the same code. The primary abstractions that need a little bit of wrapping are the `Worker`, `Agent`, `Unit`, and `Requester`. These requirements and high level abstraction reasoning are included below, while explicit implementation requirements are provided in the "How to make a new `CrowdProvider`" section.

### `Worker`
The `Worker` is responsible for keeping long-term track of a worker's individual identity as displayed by a crowd provider. Keeping the worker lets us report statistics about individual workers, as well as set up qualifications that might be more relevant than a provider could have preset. From the `CrowdProvider` perspective, different crowd providers may have different methods for identifying their workers. They may also have different methods for blocking, unblocking, qualifying, and bonusing workers. In order for Mephisto to be able to handle these actions, the `<Crowd>Worker` must abstract these. 

If the crowd provider is capable of assigning qualifications to a worker to prevent them from working on tasks they are not eligible for, you can implement `grant_crowd_qualification` and `revoke_crowd_qualification` to sync qualifications between the crowd provider and Mephisto. You'll also need to implement the `delete_qualification` method in the base `<Crowd>Provider` class if you want to be able to cleanup qualifications you've removed from Mephisto. Depending on the provider, `setup_resources_for_task_run` or `<Crowd>Unit` are the correct locations to actually register required qualifications for a task.

### `Agent`
The `Agent` is responsible for keeping track of a `Worker`'s work on a specific `Unit`. As such, it's used for approving, rejecting, and keeping track of status. Furthermore, it may be required that Mephisto tells a `CrowdProvider` that a worker has completed the task, so this must be captured as well. `<Crowd>Agent` handles all of these abstractions.

### `Unit`
The `Unit` is responsible for keeping track of portions of an `Assignment` that need to be assigned, through the entire process of them being assigned and worked on. From a high level, they are the `Assignment`-side point of entry into finding work. For the purpose of abstraction, the `Unit` needs to be able to keep track of it's remote counterpart (whatever thing we assign the worker from the crowd provider's perspective). It also needs to be able to actually _deploy_ the task to be made available through the crowd provider, and potentially expire it when it should be taken offline. `<Crowd>Unit` handles these abstractions.

### `Requester`
The `Requester` is responsible for providing the account access to be able to launch tasks. As such, any credential creation and management needs to be hidden behind the `<Crowd>Requester` so that Mephisto doesn't need to know the implementation details.

## Existing Providers
The providers we currently support are listed below:

### MTurkProvider
Provides an interface for launching tasks on MTurk and keeping track of workers and work there.

### SandboxMTurkProvider
A specific interface for launching tasks on the MTurk sandbox

(TODO) Can we bundle this into the `MTurkProvider` and make it so that providers have a TEST/SANDBOX mode bundled in? This would clarify how the testing utilities work, without needing to publish real tasks.

### LocalProvider (TODO)
An interface that allows for launching tasks on your local machine, allowing for ip-address based workers to submit work.

### MockProvider
An implementation of a provider that allows for robust testing by exposing all of the underlying state to a user.

## How to make a new `CrowdProvider`
Both the `MockProvider` and `MTurkProvider` are strong examples of implementing a provider. Important implementation details are captured below.

### `<Crowd>Provider`
The `CrowdProvider` implementation is mostly a place to centralize all of the components for this provider, and as such it should set `UnitClass`, `RequesterClass`, `WorkerClass`, and `AgentClass`. Beyond this it should implement the following:
- `initialize_provider_datastore`: This method should return a connection to any of the data required to keep tabs on the crowd provider. Ideally it should store important information to disk somehow (such as in a SQL database).
- `setup_resources_for_task_run`: This method is called prior to launching a task run, and should setup any kind of details with the provider that are required. For instance, this might register the task before requesting instances, find and register required qualifications, or do any other required prep work such as setting up listeners.

### `<Crowd>Worker`
The `<Crowd>Worker` implementation needs to handle worker interactions, generally from the perspective of a requester:
- `bonus_worker`: Provide the worker a bonus for the given reason, optionally attached to a unit. Return a tuple of `False` with an error reason if the operation can't be performed, and `(True, "")` otherwise.
- `block_worker`: Block the given worker, optionally based on their work on a unit, and from a specific requester. Return a tuple of `False` with an error reason if the operation can't be performed, and `(True, "")` otherwise.
- `unblock_worker`: Unblock the worker from a specific requester. Return a tuple of `False` with an error reason if the operation can't be performed, and `(True, "")` otherwise.
- `is_blocked`: Provide whether or not this worker is blocked by the given `Requester`.
- `is_eligible`: Determine if the worker is eligible to work on the given `TaskRun`.


### `<Crowd>Agent`
The `<Crowd>Agent` implementation needs to be able to handle the following interactions:
- `new_from_provider_data`: As different providers may give different information upon the creation of an agent (which occurs when a worker accepts a unit), this information is sent through from the server via whatever is packaged in `wrap_crowd_source.js`. You can then store this into the provider datastore and return an `Agent`.
- `approve_work`: Tell the crowd provider that this work is accepted. (If allowed)
- `reject_work`: Tell the crowd provider that this work is rejected (if allowed), with the provided feedback `reason`.
- `get_status`: Return the current agent's status according to the crowd provider (if this state is automatically tracked by the crowd provider, and can be queried). Defaults to whatever status updates the `WorkerPool` can provide.
- `mark_done`: Tell the crowd provider that the task this agent is working on is now complete (if required). Otherwise just mark it as so in the local database.

### `<Crowd>Unit`
The `<Crowd>Unit` implementation needs to be able to handle the following interactions:
- `get_status`: Return the status for this unit, as known by the provider.
- `launch`: Given the url of the server to point people to for this task, launch the task and make it available for crowd workers to claim.
- `expire`: Submit a request to expire the HIT, and return the time that will need to be waited in order for that request to be fulfilled (in case it is not immediate).

### `<Crowd>Requester`
The `<Crowd>Requester` mostly just needs to abstract the registration process, but the full list of functions are below:
- `register`: Given arguments, register this requester
- `get_register_args`: Return the arguments required to register one of these requesters. 
- `is_registered`: Determine if the current credentials for a `Requester` are valid.
- `get_available_budget` (Optional): return the available budget for this requester.

(TODO) maybe refactor budget? As not all requesters have budgets? Or perhaps have a few kinds of metadata?

### `wrap_crowd_source.js`
A few frontend functions are required to be sure that the backend is able to interface with frontend interactions:
- `getWorkerName()`: Return the worker name, as will be provided to as the identifier for mephisto to know who is attempting the task
- `getAssignmentId()`: Return an identifier for the specific task as represented by the provider.
- `getAgentRegistration()`: Return the data that is going to be passed to the `<Crowd>Agent`'s `new_from_provider` method. Currently the `worker_name` field is required to also set up the `<Crowd>Worker`.
- `handleSubmitToProvider()`: Tell the provider that the task is done from the frontend. Often amounts to hitting some kind of submit button after populating form data.

This file may also contain additional logic for handling things like error handling in a crowd provider-specific manner.