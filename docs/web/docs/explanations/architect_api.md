# Architects, Routers, and `mephisto-task`: The Architect API.

The Architect API is what allows Mephisto to completely abstract away the process of getting workers to operate in Mephisto tasks. In short, it aims to cover 4 primary functions:
1. `Worker`/`Agent` registration and validation
2. Seamless frontend access to `Unit` data made available on the Python side both when accepting and working on a task.
3. Method to submit completed task data to the backend when a task is complete.
4. Worker liveliness and status checking and syncing.

We also have a few additional goals, which influence design decisions:
1. Tasks without the _need_ for live interaction with the backend should be REST-ful rather than socket-based. This prevents the need to be fully connected throughout the task, reducing unexpected disconnects.
2. The system should include failsafes to allow for retries.
3. We should prioritize low latency where possible.
4. The interaction layer should be simple. 

This document aims to describe how we got from these requirements and goals to the system we have now.

## Requirements

### `Worker`/`Agent` registration
Mephisto allows for multiple stages of filtering for a worker, which leads the registration process to be staged. The complete order is listed below:
0. `CrowdProvider`-set qualifications may prevent a worker from even seeing a task.
1. `Qualification`s may be set locally that a `CrowdProvider` is not aware of. Workers not meeting these Mephisto qualifications (as set by `SharedState.qualifications`) should be filtered out.
2. Configuration requirements may be set, like `maximum_units_per_worker` or `allowed_concurrent` which could prevent a worker from completing more than a maximum number of units on a task or work on too many tasks at once respectively.
3. Of all available `Unit`s on `Assignment`s the worker hasn't yet worked on, workers may be further filtered by the user-provided `worker_can_do_unit` function.

This also provides a template of the failure conditions for a worker to be made aware of:
1. `Worker` doesn't meet the qualifications for a task.
2. `Worker` is working on too many tasks at a time.
3. `Worker` has completed the maximum amount of units for the given task, as set by the requester.
4. None of the _currently available_ units are available for `Worker` to access.

### Frontend access to backend `Unit` data
Mephisto must provide users with two key ways to provide data to a worker:
1. Setting `AssignmentData` for an `Assignment`, which define the data made available for a `Unit` on the frontend, and which may also be used to duplicate units.
2. Providing additional data _during_ a live task, including derived data from partial work. These should be both available via pull and push mechanisms.

Covering these two areas ensures that it's possible to create a broad variety of task types.

### Task data submission
Like backend data, completed task data should be able to be either tracked during the course of a task or submitted at the end, or both. This leads to two main event types:
1. Posting completed task data for a task during one of the completion points (onboarding, completing main `Unit` content)
2. Sending arbitrary task data at any point during a task (for data that needs a response, or longer forms of logging)

### Worker Liveliness and Status
Over the course of a task, there are a few key states to consider:
1. Connecting
2. Onboarding
3. Waiting (for other `Unit`s in an assignment)
4. In-Task
5. Completed (task complete, or partner disconnects)
6. Disconnected (Server disconnect, timeout, return)
7. Failed to connect (no available tasks)

We've also considered a "post-task" state after the completion of a task for surveys or related content.

The routing server is responsible for keeping track of the liveliness of individual `Agent`s. If it observes a disconnect on the socket, as well as timeouts on heartbeat packets.

Certain status transitions will come in from the main server, and the router may be responsible for cleaning up local state or caching results at this stage.

### RESTful vs Socket interactions
We've divided Mephisto tasks into two primary types, `static` and `live` tasks. The former shouldn't require backend access through the majority of the task, only during key points (starting, submission), while the latter can have direct communication throughout the task. 

Beyond just being simpler to implement, `static` tasks also have the advantage of being lenient on worker behavior; if a worker suspends progress and returns within the timeout window, they aren't penalized, even if their machine were to sleep during that window.

The Mephisto backend channels expect to communicate with the router in a certain way. Our primary `Channel` is the `WebsocketChannel`, and as such we expect to receive `Packet`s over the wire from the routing server.

## Implementation (proposed)

The core carrier for information in the Mephisto Architect API is the `Packet` class. Downstream, they act as the way to tie an `Agent` class in python to an actual human worker. 

The `Channel` is the primary way of trasmitting packets, with the `WebsocketChannel` being the main implementation Mephisto currently uses with its `Architect`s. The `ClientIOHandler` is responsible for using and interpreting packets, so it defines the key types to be handled.

### Packet Types
There are a number of different packet types used by Mephisto:
- `PACKET_TYPE_ALIVE`: Used to mark the success of a new socket connection.
- `PACKET_TYPE_SUBMIT_ONBOARDING`: Used to handle submission of onboarding. 
- `PACKET_TYPE_SUBMIT_UNIT`: Used to handle submission of a `Unit`. 
- `PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE`: Used to send any new live data to an agent.
- `PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE`: Used for the frontend to send any type of data to the backend, usually to be processed by a user-defined callback. 
- `PACKET_TYPE_REGISTER_AGENT`: Used to request a new `Agent` and `Unit` data for a specific worker on a task.
- `PACKET_TYPE_AGENT_DETAILS`: Used to respond with the details of a worker registration request.
- `PACKET_TYPE_UPDATE_STATUS`: Used by Mephisto to push a status update to the router and frontend worker.
- `PACKET_TYPE_REQUEST_STATUSES`: Used by Mephisto to poll for the current statuses for a worker.
- `PACKET_TYPE_RETURN_STATUSES`: Used by the router to return updates for all of the currently registered agents.
- `PACKET_TYPE_ERROR`: Used by the router and frontend to communicate to the python backend that an error has occurred.

### Architect Responsibilities

While this is the "Architect API" most of the responsibilities for the architect are merely pointing the `ClientIOHandler` to the correct `Channel`s for sending packets for a given client. Ultimately it is the `ClientIOHandler` that dictates the responsibilities that the transmitted messages carry:
- The `ClientIOHandler` must send a `PACKET_TYPE_ALIVE` whenever it opens a new channel (in this case, to a router).
- For `Unit` Registration, in response to a `PACKET_TYPE_REGISTER_AGENT`, the handler must return a `PACKET_TYPE_AGENT_DETAILS` with the details of an agent and it's initialization data, or the failure status for why an agent couldn't be created.
- During a `Unit` the handler must process `PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE` and direct the content to the correct handlers, and should send a `PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE` for any `Agent.send_data()` call on a live connected `Agent`. The handler must also process `PACKET_TYPE_SUBMIT_*` packets for the key transitions of a `Unit` in progress, and should respond with `PACKET_TYPE_AGENT_DETAILS` for a submit on an `OnboardingAgent`.
- Over any run, the handler should poll with `PACKET_TYPE_REQUEST_STATUS` and update local `Agent` statuses on disconnects from `PACKET_TYPE_RETURN_STATUSES`. This also acts as a heartbeat from the Python core to the router. The handler should also take `PACKET_TYPE_ERROR` and log the contents if this ever occurs.


### Router Responsibilities

The primary responsiblity of the router is to take incoming packets from client connections and direct them to the core Mephisto `ClientIOHandler` and to do the reverse as well. All packets will have a core `agent_id` field denoting either the sender or receiver of the packet, depending on the packet type. The only exception is the `PACKET_TYPE_ALIVE`, which is directed to the router and allows for any registration of an incoming connection.

Secondarily, the router is responsible for converting RESTful `POST` requests from `mephisto-task` into socket messages, and relaying the response as a standard `POST` response. This behavior is _only_ for the `PACKET_TYPE_REGISTER_AGENT`, and `PACKET_TYPE_SUBMIT_ONBOARDING` packets, and both of them will be serviced by `PACKET_TYPE_AGENT_DETAILS` responses. For these it should be listening to `POST` requests at `/register_worker`, `/submit_onboarding`, and `/submit_task`. `POST` requests to `/log_error` should result in forwarding a `PACKET_TYPE_ERROR`.

Third, the router is responsible for maintaining track of agent status, and acting as a cache for this information after disconnects. This allows for a worker to return to a task and have updated information about what has transpired, even when the main Mephisto server has cleaned up the related `TaskRunner` and live `Agent`.

Fourth, the router is responsible for serving the static `task_config.json` file, which allows the frontend to load certain details about the full task before going through any registration handshakes.

### `mephisto-task` responsibilities.

The `useMephistoTask` hook is responsible for allowing a worker to connect to a task and submit the relevant data. For this, it only needs to make `POST` requests related to the `PACKET_TYPE_SUBMIT_*` and `PACKET_TYPE_REGISTER_AGENT` events. The former should be triggered on `handleSubmit`, while the latter should trigger immediately on load.

The `useMephistoLiveTask` hook is responsible for the rest of the packets. Data packets should be sent via `sendData` and handled with the `onLiveUpdate` callback. So long as your data is json-serializable, you can send anything you want this way.

We also provide a `useMephistoRemoteProcedureTask` hook, which is a wrapper around `useMephistoLiveTask` that instead allows for making remote procedure calls from static tasks (when combined with the `RemoteProcedureBlueprint` or a similar API). Here people can make requests to the backend from an otherwise static task, and potentially receive responses and take action on them if they've registered callbacks. The only interface here is thus `makeRemoteCall`.
