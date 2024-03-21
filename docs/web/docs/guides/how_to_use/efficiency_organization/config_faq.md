# Common Configurations and FAQs

This document contains some Mephisto usage patterns that should be fairly common, as well as usage tips and other know-how.


## How do I see which architect and blueprint options are available?

To print out available task configuration options, use `mephisto wut` command.

**For the architect:**
```bash
mephisto wut architect=local

                                     Architect Arguments
╭────────────────────┬──────┬───────────┬──────────────────────────────┬─────────┬──────────╮
│ dest               │ type │ default   │ help                         │ choices │ required │
├────────────────────┼──────┼───────────┼──────────────────────────────┼─────────┼──────────┤
│ server_type        │ str  │ node      │ None                         │ None    │ False    │
├────────────────────┼──────┼───────────┼──────────────────────────────┼─────────┼──────────┤
│ server_source_path │ str  │ ???       │ Optional path to a prepared  │ None    │ False    │
│                    │      │           │ server directory containing  │         │          │
│                    │      │           │ everything needed to run a   │         │          │
│                    │      │           │ server of the given type.    │         │          │
│                    │      │           │ Overrides server type.       │         │          │
├────────────────────┼──────┼───────────┼──────────────────────────────┼─────────┼──────────┤
│ hostname           │ str  │ localhost │ Addressible location of the  │ None    │ False    │
│                    │      │           │ server                       │         │          │
├────────────────────┼──────┼───────────┼──────────────────────────────┼─────────┼──────────┤
│ port               │ str  │ 3000      │ Port to launch the server on │ None    │ False    │
╰────────────────────┴──────┴───────────┴──────────────────────────────┴─────────┴──────────╯
```

**For the blueprint:**
```bash
mephisto wut blueprint=static_task

Tasks launched from static blueprints need a source html file to display to workers,
as well as a csv containing values that will be inserted into templates in the html.

                                     Blueprint Arguments
╭───────────────────┬─────────┬────────────────────┬───────────────────┬─────────┬──────────╮
│ dest              │ type    │ default            │ help              │ choices │ required │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ block_qualificat… │ str     │ ???                │ Specify the name  │ None    │ False    │
│                   │         │                    │ of a              │         │          │
│                   │         │                    │ qualification     │         │          │
│                   │         │                    │ used to soft      │         │          │
│                   │         │                    │ block workers.    │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ tips_location     │ str     │ /Users/etesam1/Do… │ Path to csv file  │ None    │ False    │
│                   │         │                    │ containing tips   │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ onboarding_quali… │ str     │ ???                │ Specify the name  │ None    │ False    │
│                   │         │                    │ of a              │         │          │
│                   │         │                    │ qualification     │         │          │
│                   │         │                    │ used to block     │         │          │
│                   │         │                    │ workers who fail  │         │          │
│                   │         │                    │ onboarding, Empty │         │          │
│                   │         │                    │ will skip         │         │          │
│                   │         │                    │ onboarding.       │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ units_per_assign… │ int     │ 1                  │ How many workers  │ None    │ False    │
│                   │         │                    │ you want to do    │         │          │
│                   │         │                    │ each assignment   │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ extra_source_dir  │ str     │ ???                │ Optional path to  │ None    │ False    │
│                   │         │                    │ sources that the  │         │          │
│                   │         │                    │ HTML may refer to │         │          │
│                   │         │                    │ (such as          │         │          │
│                   │         │                    │ images/video/css… │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ data_json         │ str     │ ???                │ Path to JSON file │ None    │ False    │
│                   │         │                    │ containing task   │         │          │
│                   │         │                    │ data              │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ data_jsonl        │ str     │ ???                │ Path to JSON-L    │ None    │ False    │
│                   │         │                    │ file containing   │         │          │
│                   │         │                    │ task data         │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ data_csv          │ str     │ ???                │ Path to csv file  │ None    │ False    │
│                   │         │                    │ containing task   │         │          │
│                   │         │                    │ data              │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ task_source       │ str     │ ???                │ Path to source    │ None    │ True     │
│                   │         │                    │ HTML file for the │         │          │
│                   │         │                    │ task being run    │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ preview_source    │ unknown │ ???                │ Optional path to  │ None    │ False    │
│                   │         │                    │ source HTML file  │         │          │
│                   │         │                    │ to preview the    │         │          │
│                   │         │                    │ task              │         │          │
├───────────────────┼─────────┼────────────────────┼───────────────────┼─────────┼──────────┤
│ onboarding_source │ unknown │ ???                │ Optional path to  │ None    │ False    │
│                   │         │                    │ source HTML file  │         │          │
│                   │         │                    │ to onboarding the │         │          │
│                   │         │                    │ task              │         │          │
╰───────────────────┴─────────┴────────────────────┴───────────────────┴─────────┴──────────╯

Additional SharedTaskState args from SharedStaticTaskState
# ... snipped ...
```


## How do I manage multiple jobs? How do I keep them separate?

Mephisto is designed to be able to aggregate tasks using their `mephisto.task.task_name`. This value is an identifier used to designate when a number of related `TaskRun`s should be reviewed in the same bucket. It is a standard practice amongst our early users to group tasks by related task names, and then be able to query specific setups like the following:

```
my-new-task-local-testing
my-new-task-pilot-1
my-new-task-pilot-2
my-new-task-jan-2020-runs
```

You can use `task_name` to provide fairly expressive metadata about a specific run or group of runs, such that it's easy to refer to them later.

At the moment this parameter is used heavily in our review scripts, and future aggregators will rely on either knowing the `task_name` for a group of `TaskRun`s, or a specific `task_run_id` to get a specific `TaskRun`.


## How do I batch tasks to handle server bandwidth limitations?

By default, Mephisto makes all of the `Unit`s in a `TaskRun` available from the moment you launch it, at the same time. This can cause problems if you end up with an influx of thousands of workers hitting the one routing server launched by the `Architect`, or when your backend server is handling many `Assignment`s and their relevant `Blueprint`'s `TaskRunner`s.

If you have a compute-heavy task, or you want to run in a low resource setup, you can trade bandwidth for uptime by having Mephisto artificially limit the number of `Unit`s that are available simulaneously. This will ensure that not more than a certain number of workers can possibly be accessing your task at a time. This value is controlled via the `mephisto.task.max_num_concurrent_units` hydra argument. By default, it is set to 0, which is unlimited. It is not to be confused with the `mephisto.task.allowed_concurrent` argument, which instead controls the maximum number of `Unit`s that an individual `Worker` can do at once.

At the moment we suggest a limit of 30-50 for Live tasks and 250-500 for static tasks, given the typical setup of a heroku server and a medium-spec machine running Mephisto. You can tweak this limit as you find out the capabilities of your setup.


## How do I shut down manually? How can I clean up after something goes wrong?

Generally, Mephisto handles the clean-up process when things are shutting down normally. In the case of a catastrophic failure (like a power outage) or a situation where you need to kill a job (perhaps you launched with the wrong parameters), there are different things you need to do.

If you want to end a job early, you should be pressing Ctrl-C **ONCE** in almost all cases. This signals to Mephisto that the job should be shutdown, and pulls any available tasks off of the `CrowdProvider`. It will then _wait_ for any jobs that have already been accepted to be either submitted or returned, and _then_ it will shutdown.

If you must end the job even sooner, you *can* (but generally shouldn't) press Ctrl-C again to tell Mephisto to pull things down immediately. This should only be done after Mephisto tells you it is now waiting for jobs to finish before shutting down. This will finish up the clean up job and end in-flight tasks, then shut down the server and everything.

If you happen to press Ctrl-C again, or find things unexpectedly quit for some other reason (like power failure), then it's your responsibility to clean up. We provide scripts to assist in this where possible, like in `mephisto/scripts/mturk/`, but don't yet have all of them together. You may, for instance, find that a Heroku server is still running after being a bit to eager on the shutdown, but for now you'll have to manually shut it down with their CLI or website.


## Why is my TaskRun not finishing? It's running forever but no data is coming in...

If Mephisto is stalling forever, and no data is coming in, it's possible that either Mephisto is stuck with an active job, or that the `CrowdProvider` isn't showing any data. See if is only printing logs about tracking a currently running job, and nothing about requests from new workers or starting new tasks. If this is the case, you should verify that the server deployed by your architect is running, and that the `CrowdProvider` is actually hosting your tasks.

Note, for MTurk tasks, it's not possible to check on MTurk the status of something launched via botocore using their web interface. For this, use the script for finding outstanding hit statuses at `mephisto/scripts/mturk/print_outstanding_hit_status.py`. If no tasks are available or pending, you can safetly shut down the job.


## My question isn't answered here, where should I look for info?

Try using the `mephisto wut` cli tool to dig for more information about specific configuration arguments. If you've read through our documentation so far and haven't found the information you're looking for, feel free to open up an issue! It's possible your question may be our next entry in this list, or at least that we can do a better job directing people to the resources we already have.
