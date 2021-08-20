# Tools
The tools directory contains helper methods and modules that allow for lower-level access to the Mephisto data model than the clients provide. These may be useful for creating custom workflows and scripts that are built on Mephisto.

At the moment this folder contains the following:
- `MephistoDataBrowser`: The `MephistoDataBrowser` is a convenience tool for accessing all of the units and data associated with a specific task run or task name. It is generally used when reviewing or compiling data.
- `scripts.py`: The methods available in `scripts.py` are to be used in user scripts that rely on Mephisto. At the moment, these scripts allow for easy configuration of a database as well as augmentation of a script config for use in a Mephisto `TaskRun`. 

## `MephistoDataBrowser`
The `MephistoDataBrowser` at the moment can handle the job of getting all `Unit`s that are associated with a given task or task run. They can also retrieve the relevant data about a `Unit`, including the work done for that `Unit`, if the `Unit` is completed.

It has three usable methods at the moment:
- `get_units_for_run_id`: This will return a list of all final `Unit`'s associated with the given `task_run_id`. These will all be in a terminal state, such as `COMPLETED`, `ACCEPTED` or `REJECTED`. Units that are still in flight will not appear using this method.
- `get_units_for_task_name`: This will go through all task runs that share the given `task_name`, and collect their units in the same manner as `get_units_for_run_id`.
- `get_data_from_unit`: When given a `Unit` that is in a terminal state, this method will return data about that `Unit`, including the Mephisto id of the worker, the status of the work, the data saved by this `Unit`, and the start and end times for when the worker produced the data.

## `scripts.py`
This file contains a few helper methods for running scripts relying on the `MephistoDB`. They are as follows:
- `get_db_from_config`: This method takes in a hydra-produced `DictConfig` containing a `MephistoConfig` (such as a `RunScriptConfig`), and returns an initialized `MephistoDB` compatible with the configuration. Right now this exclusively leverages the `LocalMephistoDB`.
- `augment_config_from_db`: This method takes in a `RunScriptConfig` and a `MephistoDB`, parses the content to ensure that a valid requester and architect setup exists, and then updates the config. It also has validation steps that require user confirmation for live runs. It returns the updated config.
- `load_db_and_process_config`: This is a convenience method that wraps the above two methods, loading in the appropriate `MephistoDB` and using it to process the script. It returns the db and a valid config.