# Mephisto
This is the main package directory, containing all of the core workings of Mephisto. The breakdown is as following:

- `client`: Contains interfaces for using Mephisto at a very high level. Primarily comprised of the python code for the cli and 
- `core`: Contains components that operate on top of the data_model layer
- `data_model`: Contains the data model components as described in the architecture document, as well as the base classes for all the core abstractions.
- `providers`: contains implementations of the `CrowdProvider` abstraction
- `scripts`: contains commonly executed convenience scripts for Mephisto users
- `server`: contains implementations of the `Architect` and `Blueprint` abstractions.
- `tasks`: an empty default directory to work on your own tasks
- `utils`: unorganized utility classes that are useful in scripts and other places
- `webapp`: contains the frontend that is deployed by the main client

## Discussions

Changes to this structure for clarity are being discussed in [#285](https://github.com/facebookresearch/Mephisto/issues/285).