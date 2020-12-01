# MephistoDB implementations
This folder contains implementations of the `MephistoDB` abstraction. 

## `LocalMephistoDB`
An implementation of the Mephisto Data Model outlined in `MephistoDB`. This database stores all of the information locally via SQLite. Some helper functions are included to make the implementation cleaner by abstracting away SQLite error parsing and string formatting, however it's pretty straightforward from the requirements of MephistoDB.
