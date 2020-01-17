# CrowdProviders
The providers directory is home to the existing providers for Mephisto. This file describes high level what crowd providers do, important details on existing providers, and how to create a new `CrowdProvider` for an existing crowdsourcing service.

## Implementation Details
`CrowdProvider`s in short exist to be an abstraction layer between Mephisto and wherever we're sourcing the crowdwork from. Using `CrowdProvider`s lets Mephisto launch the same tasks all over the place using the same code. The primary abstractions that need a little bit of wrapping are the `Worker`, `Agent`, `Unit`, and `Requester`. These requirements and high level abstraction reasoning are included below, while explicit implementation requirements are provided in the "How to make a new `CrowdProvider`" section.

### `Worker`
The `Worker` is responsible for keeping long-term track of a worker's individual identity as displayed by a crowd provider. Keeping the worker lets us report statistics about individual workers, as well as set up qualifications that might be more relevant than a provider could have preset. From the `CrowdProvider` perspective, different crowd providers may have different methods for identifying their workers. They may also have different methods for blocking, unblocking, qualifying, and bonusing workers. In order for Mephisto to be able to handle these actions, the `<Crowd>Worker` must abstract these.

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

### LocalProvider
An interface that allows for launching tasks on your local machine, allowing for ip-address based workers to submit work.

(TODO) IMPLEMENT THIS

### MockProvider
An implementation of a provider that allows for robust testing by exposing all of the underlying state to a user.

## How to make a new `CrowdProvider`
