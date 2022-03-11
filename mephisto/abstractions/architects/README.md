# architects
This folder contains all of the current official `Architect` implementations.

`Architect`'s contain the logic surrounding deploying a server that workers will be able to access. In many cases Mephisto is being run on compute clusters that aren't directly addressable, or in different configurations between collaborators. Mephisto should be able to run a task from start to finish regardless of the server configuration a user would like to use, and Architect's provide this capability.


# Architect
The `Architect` class is responsible for providing Mephisto with lifecycle functions for preparing, deploying, and shutting down a given server. It's also responsible with providing access to the user via a `Channel`, which defines an interface of callbacks for incoming messages and a function for outgoing messages. It should define the following things in order to operate properly:

- `ArgsClass`: A dataclass that implements `ArchitectArgs`, specifying all of the configuration arguments that the `Architect` uses in order to properly initialize.
- `get_channels`: A method that will return a list of initialized `Channel`'s that the ClientIOHandler will need to communicate with to manage running a task. Returns a list to handle cases where an `Architect` is communicating with multiple servers in a distributed setup.
- `prepare`: Prepare any files that will be used in the deploy process. Should return the location of the prepared server files.
- `deploy`: Launch the server (if necessary) and deploy the prepared task files such that the server will be able to serve them. Return the server URL for this task, such that Mephisto can point workers to it.
- `cleanup`: Clean up any files that were used in the deploy process that aren't necessarily useful for later
- `shutdown`: Shut down the server (if necessary) or otherwise take the specific task url expected to point to this Mephisto task run offline.
- `download_file`: Save the file that is stored on the server with a given filename to the local save directory provided. Only required by `Architect`'s that aren't able to pass a file through the `Channel` directly.

## Lifecycle

During initialization, Mephisto calls `assert_task_args` and expects the `ArchitectClass` to be able to pass through any arguments specified by the `ArgsClass`, raising an exception if there are any configuration problems. After this point, Mephisto will initialize the `Architect` with the validated config.

Initially Mephisto will call `prepare` to give the `Architect` a chance to collect any relevant files required to run the server. It will give the `Blueprint` a chance to add additional files to this folder before the deploy.

Next, Mephisto will call `deploy` and then `get_channels`. This should ensure that there is an external server, and that Mephisto has a way to communicate with it through a `Channel`. Only after this is met, it will publish tasks to the crowd provider.

Once the task is done, or if it is cancelled or an error occurs, Mephisto will call `shutdown`, which is the signal for the `Architect` to clean up both local resources and remote resources related to this task.

# Implementations
## LocalArchitect
The `LocalArchitect` implementation works by running a `node` server on the local machine at the given port in a background process. It communicates over websockets with the `WebsocketChannel`, and requires that there's a directory where node is actively running in. The particular node server is the baseline `router` implementation available in the `router/node` folder.

## HerokuArchitect
The `HerokuArchitect` implementation works by getting access to the `heroku` cli, preparing a directory of what to deploy on that server, and then pushing it along. It communicates over the `WebsocketChannel`. This also relies on the node server implementation available in the `router/node` folder.

You can specify Heroku configuration variables in `hydra` using your config file:
```
#@package _global_
mephisto:
  architect:
    heroku_config_args:
      ONE_ARGUMENT: something
      ANOTHER_ARGUMENT: something else
```

## MockArchitect
The `MockArchitect` is an `Architect` used primarily for testing. To test Mephisto lifecycle, you can choose `should_run_server=False`, which just leads to the lifecycle functions marking if they've been called. Setting `should_run_server=True` can be used to automatically test certain flows, as it launches a Tornado server for which every packet and action sent through it can be scripted.

# Discussions

Currently the abstraction around `prepare` and `deploy` should be a little more rigid, defining the kinds of files that tasks should be able to deploy, where to expect to find them, etc. At the moment, this API is somewhat unclear, and while this is okay with the current set of `Architect`'s, future ones may not be as clear on this capability.

It's unclear if `cleanup` should be called immediately when the server is deployed (freeing space) or only after a task has been fully reviewed and archived following the review flow. It's possible that the deciding factor should be based on if the `Blueprint` is even registered to use the review flow at all.