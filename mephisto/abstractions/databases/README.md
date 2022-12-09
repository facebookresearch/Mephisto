# MephistoDB implementations
This folder contains implementations of the `MephistoDB` abstraction. Databases can currently be configured using the `mephisto.database._database_type` flag.

## `LocalMephistoDB`
Activated with `mephisto.database._database_type=local`. An implementation of the Mephisto Data Model outlined in `MephistoDB`. This database stores all of the information locally via SQLite. Some helper functions are included to make the implementation cleaner by abstracting away SQLite error parsing and string formatting, however it's pretty straightforward from the requirements of MephistoDB.

## `SingletonMephistoDB` <default>
This database is best used for high performance runs on a single machine, where direct access to the underlying database isn't necessary during the runtime. It makes no guarantees on the rate of writing state or status to disk, as much of it is stored locally and in caches to keep IO locks down. Using this, you'll likely be able to get up on `max_num_concurrent_units` to 150-300 on live tasks, and upwards from 500 on static tasks.

At the moment this DB acts as a wrapper around the `LocalMephistoDB`, and trades off Mephisto memory consumption for writing time. All of the data model accesses that occur are cached into a library of singletons, so large enough tasks may have memory risks. This allows us to make clearer assertions about the synced nature of the data model members, but obviously requires active memory to do so.