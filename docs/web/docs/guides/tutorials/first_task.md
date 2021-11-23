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
We'll dig into how this works shortly. 

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

### 2.3 Using yaml configurations

TODO describe how to use `task_name`, and perhaps `data_csv`. Use these in a custom `conf` file.

> **Tip**: You can reuse common configurations by [associating them with a profile](../how_to_use/efficiency_organization/reusing_configs). Usually these contain `Provider` and `Architect` arguments, as these usually aren't related to a specific task.

## Task Breakdown

Now that you've gotten a task running, this section discusses the components of the run script that cause the behavior you observed.

### `Unit` creation explained
When stepping through this task the first time, you ended up working on four `Unit`s as two different `Worker`s. 

## Step 1. Run your first task (locally)

```bash
$ cd examples/simple_static_task
$ python static_test_script.py
```

This will launch a local HTTP server with the task hosted.
You can then navigate to the task in your browser to complete the task.

To view an instance of a task, look for a print log such as this:

```
[2020-10-30 10:55:26,719][mephisto.providers.mock.mock_unit][INFO] - Mock task launched: localhost:3000 for preview, localhost:3000/?worker_id=x&assignment_id=20 for assignment 10
```

and navigate to the URL that includes parameters (ex. `localhost:3000/?worker_id=x&assignment_id=20`).

For tasks that requires two workers, such as a turn-based dialogue task, you will need to have two browser windows open at once, connected with different `worker_id` and `assignment_id` URL parameters. 


> **TIP:**
> By default, tasks are run using a "local" architect, and a "mock" requester.
> The "local" architect is reponsible for running a server on your local machine
> to host the task, and the "mock" requester is a dummy account since we won't
> be using an external crowd-provider platform such as mTurk to launch the task.
> 
> In the next step, we'll show you how to override these defaults so that you can
> host the task on Heroku and run it on mTurk instead.

## Step 2. Run the same task again (but now on mTurk!)

> Note: The Mephisto process must remain running when in-use, so you must leave your machine running to be able to access a task.

1. First, you'll first need to setup a new requester. Since we're now running on an external platform instead of locally, we'll need to setup an "mturk" requester to use instead of the dummy "mock" requester that we used previously to run locally. A new requester can be setup via the Mephisto CLI (make sure to replace `$ACCESS_KEY` and `$SECRET_KEY` below):

```bash
$ mephisto register mturk \
        name=my_mturk_user \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

You can choose any name here instead of `my_mturk_user` - this will be the id that you later refer to when using that requester.

For an `mturk_sandbox` requester, you should suffix the requester name with *"_sandbox"*, e.g.: `my_mturk_user_sandbox`.

Here's an example of setting up an "mturk_sandbox" requester:

```bash
$ mephisto register mturk_sandbox \
        name=my_mturk_user_sandbox \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY

Registered successfully.
```

Note that registering a sandbox user will not create a new entry in your `~/.aws/credentials` file if it's for the same account as your production user, as sandbox and prod use the same access keys.

2. Next, let's run the task script again, but this time we'll override the requester name and change the architect type to use [Heroku](https://www.heroku.com/). (You can find all of the architects currently supported [here](https://github.com/facebookresearch/Mephisto/tree/main/mephisto/abstractions/architects).)

```bash
$ cd examples/simple_static_task
$ python static_test_script.py mephisto/architect=heroku mephisto.provider.requester_name=my_mturk_user_sandbox
Locating heroku...
INFO - Creating a task run under task name: html-static-task-example
[mephisto.operations.operator][INFO] - Creating a task run under task name: html-static-task-example
Building server files...
...

# Note: If this is your first time running with the heroku architect, you may be asked to do some one-time setup work.


# Note: my_mturk_user_sandbox is what we used to name the requester
# when we registered the mturk account in the previous step.

# The task name mentioned in the logs will be required to examine/review results of the task in Step 3. In this case, we note that the name is html-static-task-example
```
> TIP: The arguments `mephisto.provider.requester_name=my_mturk_user_sandbox` and `mephisto/architect=heroku` will tell the run script to use the "mturk_sandbox" provider and the "heroku" architect (as opposed to the default "mock" provider and "local" architect).
> 
> Notice that if we're setting a full abstraction (like the architect abstraction) we reference it with `mephisto/abstraction=val`, however when we're setting an argument, we use `mephisto.abstraction.argument=val`. This tells [Hydra](https://hydra.cc/) (the configuration library that Mephisto uses) whether we're providing an argument value or the name of a configuration to load.


## Step 3. Review results

```bash
$ cd examples/simple_static_task
$ python examine_results.py
Input task name: 
```

 Enter the task name that was output in the console logs when prompted for `Input task name:`.
 
 In the above example, you'll note that it was `html-static-task-example`.
