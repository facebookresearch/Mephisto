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

## `examine_utils.py`
This file contains a number of helper functions that are useful for running reviews over Mephisto data. We provide a high-level script for doing a 'review-by-worker' style evaluation, as well as breakout helper functions that could be useful in alternate review flows.
- `run_examine_by_worker`: This function takes a function `format_data_for_printing` that consumes the result of `MephistoDataBrowser.get_data_from_unit`, and should print out to terminal a reviewable format. It optionally takes in `task_name`, `block_qualification`, and `approve_qualification` arguments. If `task_name` is provided, the script will be run in review mode without querying the user for anything.
- `print_results`: This function takes a task name and display function `format_data_for_printing`, and an optional int `limit`, and prints up to `limit` results to stdout.
- `format_worker_stats`: Takes in a worker id and set of previous worker stats, and returns the previous stats in the format `(accepted_count | total_rejected_count (soft_rejected_count) / total count)`
- `prompt_for_options`: Prompts the user for `task_name`, `block_qualification`, and `approve_qualification`. If provided as an argument, skips. Returns these values after confirming with the user, and if blank uses `None`.

## `scripts.py`
This file contains a few helper methods for running scripts relying on the `MephistoDB`. They are as follows:
- `get_db_from_config`: This method takes in a hydra-produced `DictConfig` containing a `MephistoConfig` (such as a `TaskConfig`), and returns an initialized `MephistoDB` compatible with the configuration. Right now this exclusively leverages the `LocalMephistoDB`.
- `augment_config_from_db`: This method takes in a `TaskConfig` and a `MephistoDB`, parses the content to ensure that a valid requester and architect setup exists, and then updates the config. It also has validation steps that require user confirmation for live runs. It returns the updated config.
- `load_db_and_process_config`: This is a convenience method that wraps the above two methods, loading in the appropriate `MephistoDB` and using it to process the script. It returns the db and a valid config.
- `process_config_and_get_operator`: A convenience wrapper of the above method that _also_ creates an `Operator` too.
- `task_script`: This decorator is used to register a Mephisto script for launching task runs. It takes in either a `config` (`TaskConfig`) or `default_config_file` (yaml filename without the .yaml) argument to specify how the script is configured, and wraps a main that takes in an `Operator` and `DictConfig` as arguments.