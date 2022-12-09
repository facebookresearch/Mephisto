# Mephisto Core Abstractions
This directory contains the interfaces for the four core Mephisto abstractions (as well as subcomponents of those abstractions). Those abstractions are discussed at a high level in the [architecture overvierw doc](https://github.com/facebookresearch/Mephisto/blob/main/docs/architecture_overview.md).

Specific implementations can be made to extend the Mephisto data model to work with new crowd providers, new task types, and new backend server architectures. These four primary abstractions are summarized below, but other sections go more in-depth.

### `Architect`
An [`Architect`](https://github.com/facebookresearch/Mephisto/blob/main/mephisto/abstractions/architects/README.md#architect) is an abstraction that allows Mephisto to manage setup and maintenance of task servers for you. When launching a task, Mephisto uses an `Architect` to build required server files, launch that server, deploy the task files, and then later shut it down when the task is complete. More details are found in the `abstractions/architects` folder, along with the existing `Architects`.

Architects also require a `Channel` to allow the `ClientIOHandler` to communicate with the server, and are expected to define their own or select a compatible one from the ones already present.

### `Blueprint`
A [`Blueprint`](https://github.com/facebookresearch/Mephisto/blob/main/mephisto/abstractions/blueprints/README.md#overview) is the essential formula for running a task on Mephisto. It accepts some number of parameters and input data, and that should be sufficient content to be able to display a frontend to the crowdworker, process their responses, and then save them somewhere. It comprises of extensions of the `AgentState` (data storage), `TaskRunner` (actual steps to complete the task), and `TaskBuilder` (resources to display a frontend) classes. More details are provided in the `abstractions/blueprints` folder, where all the existing `Blueprint`s live.

### `CrowdProvider`
A [`CrowdProvider`](https://github.com/facebookresearch/Mephisto/blob/main/mephisto/abstractions/providers/README.md#implementation-details) is a wrapper around any of the required functionality that Mephisto will need to utilize to accept work from workers on a specific service. Ultimately it comprises of an extension of each of `Worker`, `Agent`, `Unit`, and `Requester`. More details can be found in the `abstractions/providers` folder, where all of the existing `CrowdProvider`s live.

### `MephistoDB`
The [`MephistoDB`](https://github.com/facebookresearch/Mephisto/blob/main/mephisto/abstractions/databases/README.md) is an abstraction around the storage for the Mephisto data model, such that it could be possible to create alternate methods for storing and loading the kind of data that mephisto requires without breaking functionality.