# Mephisto
This is the main package directory, containing all of the core workings of Mephisto. They roughly follow the divisions noted in the [architecture overview doc](https://github.com/facebookresearch/Mephisto/blob/main/docs/architecture_overview.md#agent). The breakdown is as following:

- `abstractions`: Contains the interface classes for the core abstractions in Mephisto, as well as implementations of those interfaces. These are the Architects, Blueprints, Crowd Providers, and Databases.
- `client`: Contains user interfaces for using Mephisto at a very high level. Primarily comprised of the python code for the cli and the web views.
- `data_model`: Contains the data model components as described in the architecture document. These are the relevant data structures that build upon the underlying MephistoDB, and are utilized throughout the Mephisto codebase.
- `operations`: Contains low-level operational code that performs more complex functionality on top of the Mephisto data model.
- `scripts`: Contains commonly executed convenience scripts for Mephisto users.
- `tools`: Contains helper methods and modules that allow for lower-level access to the Mephisto data model than the clients provide. Useful for creating custom workflows and scripts that are built on Mephisto.
