# channels
This folder contains the base `Channel` class, and some implementations (well, one for now).

# Channel
The channel class acts as the abstraction layer that allows servers with different configurations to still communicate with Mephisto. It is an interface that the `Supervisor` class knows how to communicate with, and different `Architect`'s may need specialized methodology to surface mephisto events to the user. `Architect` classes should be able to return a `Channel` to the `Supervisor` that will be used to communicate with any users that connect to Mephisto via that architect. 

The Channel class has five primary methods:
- `open`: Does whatever is necessary to connect the local python `Channel` with the remote server to communicate.
- `is_alive`: Should return whether or not the currently open connection is alive. Should remain `False` until after an `open` call successfully connects with the server.
- `close`: Close the `Channel`, and ensure that all threads and resources used for the it have been cleaned up properly.
- `is_closed`: Should return `True` only if `close` has been called for this channel, or the channel has closed itself due to an error.
- `send`: Is given a `Packet` object, and should pass it along to the intended recipient and return `True`. If there's a transient error, should return `False`. If there's a serious error, it should do something to set `is_alive` to `False` and also return `False`.

It also takes in three callback methods:
- `on_channel_open`: Should be called when the channel is first alive, telling the Supervisor that it's okay to send a registration message.
- `on_catastrophic_disconnect`: Should be called when the `Channel` believes that it is no longer able to communicate with the server.
- `on_message`: Should parse incoming messages from the server into `Packet` objects, and then call this callback with that object.

## Lifecycle

The basic lifecycle of a `Channel` surfaces when a `Supervisor` is given a job with `register_job`. It reaches out to the `Architect` to get a method to connect to the users. After calling `open` it waits until the first `is_alive` call returns `True`, then begins running. The `Channel` should also call `on_channel_open` the first time it's certain that the 

While the server is running, it should take incoming messages from the server and convert them to the `Packet` format, and pass them along using `on_message`. It should take outgoing message `Packet`'s with `send` and pass them to the server.

Once the task completes its run, or if it's interrupted or a serious error occurs, Mephisto will call `close` on all channels. At this point the `Channel` should clean up resources.

## Retriability + Failure handling

Ultimately if the `Channel` that Mephisto is communicating using dies, the Mephisto process needs to suspend the current run, shutdown, and clean up. As such, we leave it up to the `Channel` implementation to determine if the connection is still stable enough to be running. `is_alive`, the retriability of `send`, and `on_catastraphic_disconnect` covers the full freedom for a `Channel` to be able to signal to Mephisto that a task is no longer salvageable.

Another way to visualize the flow for this would be to try to `send` a message, and upon failure, launch a thread that tries to fix the issue, then return `False` for the `send` call. Mephisto will wait for `is_alive` to be true before retrying. If the `Channel` succeeds in re-establishing a connection, then the retries will eventually go through. If the `Channel` believes that something is *really* wrong, it should call `on_catastraphic_disconnect`.

# WebsocketChannel

The `WebsocketChannel` is a `Channel` implementation that relies on a websocket app to handle incoming and outgoing messages. This application is run inside of a thread, and cleaned up on closure. It is usable on all systems that can maintain stable websocket-based connections, and with all `Architect`'s that can communicate over a socket.