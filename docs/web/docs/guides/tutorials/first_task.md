---
sidebar_position: 1
---

# Running your first task

So you want to launch your first task. Thankfully Mephisto makes this fairly easy! We'll launch an HTML-based task as a way to get you started. This guide assumes you've worked through [the quickstart](../quickstart), so begin there if you haven't.

## 1. Launching with default arguments

### 1.1 Run the task

To get started, you can launch a task by executing a run script. For instance, let's try the simple static HTML task:

```bash
$ cd examples/simple_static_task
$ python static_test_script.py
```

This will launch a local HTTP server with the task hosted, based on the default configuration options:
```yaml
# hydra_configs/conf/example.yaml
defaults:
  - /mephisto/blueprint: static_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
```
We'll dig into *how* this works [later](#33-default-abstraction-usage). 

### 1.2 Access the task

By default, the task should be hosted at `localhost:3000`. This default is set by the `LocalArchitect`, which is used based on the `- /mephisto/architect: local` line above. Navigating to this address should show you the preview view for the task.

Actually being able to access this task is done by providing `worker_id` and `assignment_id` URL params, like `localhost:3000/?worker_id=x&assignment_id=1` The `MockProvider` interprets these to be a test worker, which you can use to try out tasks. 

Try navigating here and completing a task by selecting a value (no need to use the file upload). After hitting submit you'll note that the window alerts you to the data that was sent to the Mephisto backend.

To work on another task, you'll want to change the `assignment_id` in your url. This will let `Worker` "x" work on another task. Complete and submit this too.

If you try to work on another task, you'll note that the system states you've worked on the maximum number of tasks. On this task, this is because Mephisto has launched the same two tasks twice to attempt to get different workers to complete them, and as "x" you've already completed both tasks. More on this [later.](#unit-creation-explained)

If you change to another `worker_id`, however, you can complete two more tasks. Do this and the Mephisto process should shut down cleanly. 


### 1.3 Reviewing tasks

At this stage, we've collected data, and we'd like to review it. Here we'll do so with the command line interface, using the review script, which is in the same directory:
```bash
$ python examine_results.py
Do you want to (r)eview, or (e)xamine data? Default examine. Can put e <end> or e <start> <end> to choose how many to view
>> r
Input task name: 
```

Here we can enter the default task name for this task, `html-static-task-example` to see the results. You can also leave the two qualifications blank, as we aren't dealing with these yet.

```
Input task name: html-static-task-example
If you'd like to soft-block workers, you'll need a block qualification. Leave blank otherwise.
Enter block qualification: 
If you'd like to qualify high-quality workers, you'll need an approve qualification. Leave blank otherwise.
Enter approve qualification: 
Starting review with following params:
Task name: html-static-task-example
Blocking qualification: None
Approve qualification: None
Press enter to continue... 
```
After pressing enter, you'll be able to take action on some of the incoming tasks. You can `(a)ccept, (r)eject, (p)ass` using `a`, `r`, or `p`, using the caps version to apply to all the `Unit`s for a specific worker. Passing is used for work you think was attempted legitimately, but may have not been done 
```
Reviewing for worker x, (1/2), Previous (First time worker!) (total remaining: 4)
-------------------
Worker: x
Unit: 4455
Duration: 288
Status: completed
Character: Loaded Character 1
Description: I'm a character loaded from Mephisto!
   Rating: passable
   Files: []
   File directory ...
```
Review all four tasks (two from each of your test workers), and the script will close. Congrats on finishing your first complete batch!

## 2. Changing some defaults!

Mephisto uses [Hydra](https://hydra.cc/) for our task configuration. As such you can use any of the Hydra methods for configuration. Of course, to configure you have to know your options.

### 2.1 Discovering options with `mephisto wut`

Mephisto configuration options can be inherited from a number of different locations, so it can be difficult to track down all available arguments on your own. We provide the `mephisto wut` cli tool to make this process simpler. For instance, knowing that we're launching a `static_task` with the `local` architect (as we saw [here](#11-run-the-task)), we can examine these for configuration options.

**For the architect:**
```bash
$ mephisto wut architect=local

dest                type    default    help                                    choices    required
------------------  ------  ---------  --------------------------------------  ---------  ----------
server_type         str     node       None                                    None       False
server_source_path  str     ???        Optional path to a prepared server      None       False
                                       directory containing everything needed
                                       to run a server of the given type.
                                       Overrides server type.
hostname            str     localhost  Addressible location of the server      None       False
port                str     3000       Port to launch the server on            None       False
```

**For the blueprint:**
```bash
$ mephisto wut blueprint=static_task
Tasks launched from static blueprints need a source html file to display to workers, as well as a csv containing values that will be inserted into templates in the html. 
dest                      type     default    help                                      choices    required
------------------------  -------  ---------  ----------------------------------------  ---------  ----------
block_qualification       str      ???        Specify the name of a qualification used  None       False
                                              to soft block workers.
onboarding_qualification  str      ???        Specify the name of a qualification used  None       False
                                              to block workers who fail onboarding,
                                              Empty will skip onboarding.
units_per_assignment      int      1          How many workers you want to do each      None       False
                                              assignment
extra_source_dir          str      ???        Optional path to sources that the HTML    None       False
                                              may refer to (such as
                                              images/video/css/scripts)
data_json                 str      ???        Path to JSON file containing task data    None       False
data_jsonl                str      ???        Path to JSON-L file containing task data  None       False
data_csv                  str      ???        Path to csv file containing task data     None       False
task_source               str      ???        Path to source HTML file for the task     None       True
                                              being run
preview_source            unknown  ???        Optional path to source HTML file to      None       False
                                              preview the task
onboarding_source         unknown  ???        Optional path to source HTML file to      None       False
                                              onboarding the task
Additional SharedTaskState args from SharedStaticTaskState
# ... snipped ...
```

For our given example task, the values we are using for these options are available in the `hydra_configs/conf/example.yaml` file. Let's try overriding some defaults.

### 2.2 Configuring options via the command line

As a simple starting point, we can try launching the server on a different port. Right now the default is `3000`, but with the following command we can set that ourselves:
```
python static_test_script.py mephisto.architect.port=1234
```

This should launch the same task, but now available on the port `1234` rather than `3000`.

Once we see the task is running, we can shut down with `Ctrl-C`.

> **Tip:** Shutting down Mephisto via a single `Ctrl-C` interrupt *attempts* to cleanup everything, but sometimes takes time for cleanup steps. You can skip some steps with additional `Ctrl-C` presses, but then you'll need to clean up resources yourself.

### 2.3 Using yaml configurations

While it makes sense to update some parameters on the command line while iterating, generally it's easier to extend the `conf` files directly, then apply all of the options by overriding `conf`. Try copying the `hydra_configs/conf/example.yaml` file into `hydra_configs/conf/my_config.yaml`.

```yaml
#hydra_configs/conf/my_config.yaml

#@package _global_
defaults:
  - /mephisto/blueprint: static_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
mephisto:
  blueprint:
    data_csv: ${task_dir}/data_tutorial.csv    # Lets use the tutorial data
    task_source: ${task_dir}/server_files/demo_task.html
    preview_source: ${task_dir}/server_files/demo_preview.html
    extra_source_dir: ${task_dir}/server_files/extra_refs
    units_per_assignment: 1   # And only one unit per assignment, as we're testing as one worker
  task:
    task_name: first-task-tutorial-run  # Let's change the task name
    task_title: "Test static task"
    task_description: "This is a simple test of static tasks."
    task_reward: 0.3
    task_tags: "static,task,testing"
```

Save this configuration file, and you're ready to launch again:
```bash
$ python static_test_script conf=my_config
```
You'll note that Mephisto launches the task under your new task name:
```
[...][...][INFO] - Creating a task run under task name: first-task-tutorial-run
```

> **A note on `task_name`s:**
> The `task_name` parameter is particularly important for setting up workflows. Many of Mephisto's features are shared under a specific `task_name` namespace, including review flows and unit completion maximums per worker per namespace. Later [tutorials](workflows) and [how-to guides](../how_to_use/efficiency_organization/task_organization) go more in-depth on best practices.

Navigating to a task (`localhost:3000/?worker_id=x&assignment_id=1`) should now show you a task loaded from a different data file. Completing this task will lead Mephisto to shut down cleanly.

You can now review this task with the review script again, this time providing the task name `first-task-tutorial-run`.

### 2.4 (optional) Launch live on MTurk sandbox

> Note: The Mephisto process must remain running when in-use, so you must leave your machine running to be able to access a task.

You don't need to do this step *right now*, however it's important for understanding how to take one of these tasks live. Assuming you've completed the optional steps in [the quickstart](../quickstart#optional-set-up-mturk), you can make the following changes to your config file, replacing `my_mturk_user_sandbox` with the id you used in it's place when registering initially:
```yaml
#hydra_configs/conf/my_config.yaml

#@package _global_
defaults:
  - /mephisto/blueprint: static_task
  - /mephisto/architect: heroku   # To launch live, we'll need an external server
  - /mephisto/provider: mturk_sandbox  # And an external provider
mephisto:
  provider:
    requester_name: my_mturk_user_sandbox # Or whatever ID you provided with `mephisto register mturk_sandbox`
  blueprint:
    data_csv: ${task_dir}/data_tutorial.csv
    task_source: ${task_dir}/server_files/demo_task.html
    preview_source: ${task_dir}/server_files/demo_preview.html
    extra_source_dir: ${task_dir}/server_files/extra_refs
    units_per_assignment: 1
  task:
    task_name: first-task-tutorial-run
    task_title: "Test static task"
    task_description: "This is a simple test of static tasks."
    task_reward: 0.3
    task_tags: "static,task,testing"
```
Save this configuration file, and you're ready to see your task live:
```bash
$ python static_test_script conf=my_config
```
Mephisto should print out a link to view your task on the mturk sandbox, like `https://workersandbox.mturk.com/mturk/preview?groupId=XXXXXXXXXXXXXXXX`. Navigate here and you're working on the same task, available on MTurk (on the sandbox at least)!

Complete this task, and you can review it in the same way as before.

> **Tip**: You can reuse common configurations by [associating them with a profile](../how_to_use/efficiency_organization/reusing_configs). Usually these contain `Provider` and `Architect` arguments, as these usually aren't related to a specific task.

## 3. Task breakdown

Now that you've gotten a task running, this section gives a quick overview on some of the components in the configs and `static_test_script.py` that led to the observed behaviors. The goal is to ensure you can write your own run files by the end of the tutorial sections.

### 3.1 Config registration
Mephisto wires up to configuration using standard Hydra syntax, but with both `yaml` files (for ease of writing) _and_ structured configs (for ease of documentation). Here's the config we've set up for this example, re-ordered for understanding:
```python
# static_test_script.py
from mephisto.abstractions.blueprints.static_html_task.static_html_blueprint import (
    BLUEPRINT_TYPE,
)
...

defaults = ["_self_", {"conf": "example"}]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config
TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY

register_script_config(name="scriptconfig", module=TestScriptConfig)
@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
```
In this snippet, we do a few things:
1. We import the `BLUEPRINT_TYPE` to force an import of the blueprint we intend to use with this run script. This isn't *required* for Mephisto default blueprints, but is important for custom `Blueprint`s to ensure they are loaded into the Mephisto registry.
2. We set up the default `conf` file to be `example`, which ensures that Hydra looks into `conf/example.yaml` on any run where this isn't overridden.
3. We create a `RunScriptConfig`, which is a set of options that we are allowed to set for a task. Here, we only provide a `task_dir`, which you can override on the command line with `python static_test_script.py task_dir=some/other/path`. Mostly, we use this for ensuring that the `data_csv` and other path-related variables are portable.
4. We register this config with hydra, and then have the `main` function point to this configuration. Note the `hydra_configs` value for `config_path`, which now fully explains the `hydra_configs/conf/example.yaml` path. 

With all the above, we're able to just make edits to `example.yaml` or make other configs in the `conf/` directory and route to them directly.

### 3.2 Invoking Mephisto
Mephisto itself is actually invoked just a little later:
```python
def main(cfg: DictConfig) -> None:
    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
```
Here we use the `load_db_and_process_config` helper to extract specific arguments out of your configuration (and surface warnings about incompatibilities), as well as load the correct `MephistoDB` for the task. We then initialize an `Operator` (the main entry point for running a Mephisto `TaskRun`), and run the given config, then wait for it to run. To ensure we're not frozen, the operator takes in a `log_rate` in seconds to print status messages while the run is underway.

### 3.3 Default abstraction usage
Again we can look back at the `example.yaml` file to see this setup:
```yaml
# hydra_configs/conf/example.yaml
defaults:
  - /mephisto/blueprint: static_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
```
These ensure that, when not provided other arguments, we launch this task locally using a `LocalArchitect` and `MockProvider`. With these defaults, this and other example tasks are run using a "local" architect, and a "mock" requester without arguments. The "local" architect is reponsible for running a server on your local machine to host the task, and the "mock" requester lets *you* simulate a worker without using an external crowd-provider platform such as mTurk to launch the task.

### 3.4 `Unit` creation explained
When stepping through this task the first time, you ended up working on four `Unit`s as two different `Worker`s. It's useful to understand how this happens. Taking a look at the config and data:
```yaml
# hydra_configs/conf/example.yaml

#@package _global_
defaults:
...
mephisto:
  ...
  blueprint:
    data_csv: ${task_dir}/data.csv
    ...
    units_per_assignment: 2
  task:
    ...
```
```
# data.csv
character_name,character_description
Loaded Character 1,I'm a character loaded from Mephisto!
Loaded Character 2,I'm another character loaded from Mephisto!
```

From this, we know we're loading from `data.csv`, and that this file only has two listed items. Mephisto creates an `Assignment` for each of these lines, representing a group of work for which a worker can only contribute to once. We also specify two `units_per_assignment`, meaning that Mephisto creates two `Unit`s per `Assignment`, meaning in this static case that different workers can complete the same job, usually to get inter-annotator agreement. (In some cases Mephisto can use an `Assignment` to connect multiple workers each with one `Unit` on a collaborative live task). As we had two assignments, it makes sense that each worker `x` and your second worker could only complete two tasks each.

On the second launch, we had a file with only one entry and set `units_per_assignment` to 1, which ensured that there was only a single `Unit` that needed to be completed before Mephisto shut down.
