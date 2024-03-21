---
sidebar_position: 1
---

# Running your first task

So you want to launch your first task.
Thankfully Mephisto makes this fairly easy!
We'll launch an HTML-based task as a way to get you started.
This guide assumes you've worked through [the quickstart](/docs/guides/quickstart/), so begin there if you haven't.

## 1. Launching with default arguments

Before every task run, we recommend to remove content of folder `/tmp` (in case the previous Task run didn't shut down correctly).

### 1.1 Run the task

To get started, you can launch a task by executing a run script. For instance, let's try the form-based simple task:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
  --build \
  --publish 3001:3000 \
  --rm mephisto_dc \
  python /mephisto/examples/form_composer_demo/run_task.py
```

or without using Docker

```shell
cd /mephisto/examples/form_composer_demo/
python run_task.py
```

This will launch a local HTTP server with the task hosted, based on the default configuration options:
```yaml
# examples/form_composer_demo/hydra_configs/conf/example_local_mock.yaml
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
```
We'll dig into *how* this works [later](#33-default-abstraction-usage).


### 1.2 Access the task

By default, the task should be hosted at [http://localhost:3000](http://localhost:3000) in browser. If you used the Docker command, then the URL will be [http://localhost:3001](http://localhost:3001).

This default is set by the `LocalArchitect`, which is used based on the `- /mephisto/architect: local` line above.
Navigating to this address should show you the preview view for the task.

Actually being able to access this task is done by providing `worker_id` and `assignment_id` URL params, like `localhost:3000/?worker_id=x&assignment_id=1`.
The `MockProvider` interprets these to be a test worker, which you can use to try out tasks.

Try navigating here and completing a task by selecting a value (no need to use the file upload).
After hitting submit you'll note that the window alerts you to the data that was sent to the Mephisto backend.

To work on another task, you'll want to change the `assignment_id` in your url. This will let `Worker` "x" work on another task.
Complete and submit this too.

If you try to work on another task, you'll note that the system states you've worked on the maximum number of tasks.
On this task, this is because Mephisto has launched the same two tasks twice to attempt to get different workers to complete them, and as "x" you've already completed both tasks.
More on this [later.](#unit-creation-explained)

If you change to another `worker_id`, however, you can complete two more tasks.
Do this and the Mephisto process should shut down cleanly.


### 1.3 Review task results

By this stage, we've collected data and can now review it. For your convenience, for most cases we already wrote a browser-based application to review task results.

TaskReview app even can display your task unit content as it was presented to workers. _In your own tasks you may need to write [additional react application](/docs/guides/how_to_use/review_app/enabling_original_unit_preview/) to do this, but we've already done this for you in this example._


### 1.3.1 Run TaskReview app

Use the following command to start TaskReview app:
```bash
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --rm mephisto_dc \
    mephisto review_app --host 0.0.0.0 --port 8000
```

or without using Docker

```shell
mephisto review_app
```

### 1.3.2 Access TaskReview app

You will see a message like this in your console:
```shell
2024-03-21 16:50:55,300 - werkzeug - INFO -  * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```

You can open the provided URL in browser [http://127.0.0.1:5000](http://127.0.0.1:5000).
If you used the Docker command, then the URL will be [http://localhost:8081](http://localhost:8081).

There you will see a page showing all of your completed tasks. Clicking on a task name will let you review task units completed by each worker. Upon reviewing all task units you will be redirected back to the tasks list page, where you can download task results as one JSON file.

For more details, see [Reviewing task results](/docs/guides/tutorials/review_app/).

Congrats on finishing your first complete batch!


## 2. Change some defaults

Mephisto uses [Hydra](https://hydra.cc/) for our task configuration.
As such you can use any of the Hydra methods for configuration.
Of course, to configure you have to know your options.

### 2.1 Discovering options with `mephisto wut`

Mephisto configuration options can be inherited from a number of different locations, so it can be difficult to track down all available arguments on your own. We provide the `mephisto wut` cli tool to make this process simpler. For instance, knowing that we're launching a `static_task` with the `local` architect, we can examine these for configuration options.

```bash
# show available architect options
mephisto wut architect=local
# show available blueprint options
mephisto wut blueprint=static_task
```

A list of all available values is available at [Common Configurations and FAQs](/docs/guides/how_to_use/efficiency_organization/config_faq/).

For our given example task, the values we are using for these options are available in the `hydra_configs/conf/example.yaml` file. Let's try overriding some defaults.

### 2.2 Configuring options via the command line

As a simple starting point, we can try launching the server on a different port. Right now the default is `3000`, but with the following command we can set that ourselves:
```
python run_task.py mephisto.architect.port=1234
```

This should launch the same task, but now available on the port `1234` rather than `3000`.

Once we see the task is running, we can shut down with `Ctrl-C`.

> **Tip:** Shutting down Mephisto via a single `Ctrl-C` interrupt *attempts* to cleanup everything, but sometimes takes time for cleanup steps.
> You can skip some steps with additional `Ctrl-C` presses, but then you'll need to clean up resources yourself.

### 2.3 Using yaml configurations

While it makes sense to update some parameters on the command line while iterating, generally it's easier to extend the `conf` files directly, then apply all of the options by overriding `conf`.
Try copying the `examples/form_composer_demo/hydra_configs/conf/example_local_mock.yaml` file into `examples/form_composer_demo/hydra_configs/conf/my_config.yaml`.
Also file `examples/form_composer_demo/data/simple/task_data.json` into `examples/form_composer_demo/data/simple/my_task_data.json`

```yaml
#examples/form_composer_demo/hydra_configs/conf/my_config.yaml

#@package _global_
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: local
  - /mephisto/provider: mock

mephisto:
  blueprint:
    data_json: ${task_dir}/data/simple/my_task_data.json  # Change path to your new file and change some data in it
    task_source: ${task_dir}/webapp/build/bundle.js
    task_source_review: ${task_dir}/webapp/build/bundle.review.js
    link_task_source: false
    extra_source_dir: ${task_dir}/webapp/src/static
    units_per_assignment: 3
  task:
    task_name: "My first own task"  # Change the task name
    task_title: "New title"  # Change the task title
    task_description: "In this Task, we use FormComposer feature."  # Change the task description
    task_reward: 0
    task_tags: "test,simple,form"
    force_rebuild: true
```

Save this configuration file, and you're ready to launch again:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
  --build \
  --publish 3001:3000 \
  --rm mephisto_dc \
  python /mephisto/examples/form_composer_demo/run_task.py conf=my_config
```

or without using Docker

```bash
cd /mephisto/examples/form_composer_demo/
python run_task.py conf=my_config
```

Now you'll notice that Mephisto launches your task under the new task name:
```
[...][...][INFO] - Creating a task run under task name: My first own task
```

> **A note on `task_name`s:**
> The `task_name` parameter is particularly important for setting up workflows. Many of Mephisto's features are shared under a specific `task_name` namespace, including review flows and unit completion maximums per worker per namespace. Later [guides](../workflows) go more in-depth on best practices.

Navigating to a task (`localhost:3000/?worker_id=x&assignment_id=1` or woth Docker on `3001` port) should now show you a task loaded from a different data file.
Completing this task will lead Mephisto to shut down cleanly.

You can now review this task with the review script again, this time providing the task name `My first own task`.

### 2.4 (optional) Launch your task live

So far we've been launching our task in a testing mode (with `local` architect and `mock` provider).

To make your Task page accessible to the others (e.g. external workers), you will either need to obtain a publicly accessible static IP address for you machine, or launch the task with a non-`mock` human cloud platform and a non-`local` architect.

In the below examples we consider an EC2 architect and a few common providers. This configuration is different from the testing mode:
- EC2 architect will build a temporary EC2 server in the cloud, which will:
  - serve webpages with newly assigned units of your (now publicly accessible) Task to workers on human cloud provider's platform
  - send completed task results to your machine
  - dismantle the EC2 server if the Task is terminated for whichever reason
- non-mock provider will maintain an API connection with a human cloud platform to:
  - direct workers willing to work on your Task to an EC2 webpage for their newly assigned task unit
  - monitor status of all task units currently being worked on
  - handle routine opeartions on task units and workers (expire a stalled unit; give bonus to worker; etc)

> Note: The Mephisto process must remain continuously running when in-use, so you must leave your machine running to be able to access a task.

#### 2.4.1 Launching live on MTurk sandbox

First, let's specify the API credentials:
  - Create file `docker/aws_credentials` and populate it with your AWS keys info (for EC2 architect)
  - Add your Mturk account API keys to `docker/aws_credentials` file
  - Clone file `docker/docker-compose.dev.yml` as `docker/docker-compose.local.yml`, and point its `env_file` to `envs/env.local`
  - Ensure `envs/env.local` file has a defeinition of these env variables:
      - `CYPRESS_CACHE_FOLDER`: set it to any writable folder, e.g. `/tmp`

Now we're ready to launch an example task on Mturk platform:

```shell
docker-compose -f docker/docker-compose.local.yml run \
  --build \
  --publish 3001:3000 \
  --rm mephisto_dc \
  python /mephisto/examples/form_composer_demo/run_task_dynamic_ec2_mturk_sandbox.py
```

Note that this command reads task parameters from task config file referenced within the `run_task_dynamic_ec2_mturk_sandbox.py` script.

Generally, you would want to adjust task config file to your needs.
You don't need to do this step *right now*, however it's important for understanding how to take one of these tasks live.
Assuming you've completed the optional steps in [the quickstart](/docs/guides/quickstart/#optional-set-up-mturk),
you can make the following changes to your config file, replacing `my_mturk_user_sandbox` with the id you used in it's place when registering initially:

```yaml
#examples/form_composer_demo/hydra_configs/conf/my_config.yaml

#@package _global_
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: ec2  # To launch live, we'll need an external server
  - /mephisto/provider: mturk_sandbox  # And an external provider

mephisto:
  architect:
    _architect_type: ec2
    profile_name: my_ec2_user  # Name of EC2 user
    subdomain: "0123"  # Each Task Run must have a unique subdomain
  blueprint:
    data_json: ${task_dir}/data/dynamic/task_data.json
    task_source: ${task_dir}/webapp/build/bundle.js
    task_source_review: ${task_dir}/webapp/build/bundle.review.js
    preview_source: ${task_dir}/preview/mturk_preview.html
    link_task_source: false
    extra_source_dir: ${task_dir}/webapp/src/static
    units_per_assignment: 1
  log_level: "debug"
  task:
    task_name: "Sample Questionnaire"
    task_title: "Dynamic form-based Tasks for Mturk"
    task_description: "In this Task, we use dynamic FormComposer feature."
    task_reward: 0.05
    task_tags: "dynamic,form,testing"
    assignment_duration_in_seconds: 3600
    force_rebuild: true
    max_num_concurrent_units: 1
    maximum_units_per_worker: 2
  provider:
    requester_name: my_mturk_user_sandbox  # Or whatever ID you provided with `mephisto register mturk_sandbox`
```

Save this configuration file as `examples/form_composer_demo/hydra_configs/conf/my_config.yaml`, and you will see your task go live on Mturk platform!

```shell
docker-compose -f docker/docker-compose.dev.yml run \
  --build \
  --publish 3001:3000 \
  --rm mephisto_dc \
  python /mephisto/examples/form_composer_demo/run_task_dynamic_ec2_mturk_sandbox.py conf=my_config
```

or without using Docker

```bash
cd /mephisto/examples/form_composer_demo/
python run_task_dynamic_ec2_mturk_sandbox.py conf=my_config
```

Mephisto should print out links to view your task on the mturk sandbox,
like `https://workersandbox.mturk.com/mturk/preview?groupId=XXXXXXXXXXXXXXXX`.
Navigate here and you'll be see your task live on Mturk sandbox, as if you were a worker!

Complete this task, and you can review it in the same way as usual.

> **Tip**: You can reuse common configurations by [associating them with a profile](/docs/guides/how_to_use/efficiency_organization/reusing_configs/).
> Usually these contain `Provider` and `Architect` arguments, as these usually aren't related to a specific task.


#### 2.4.2 Launching live on Prolific

First, let's specify the API credentials:
  - Create file `docker/aws_credentials` and populate it with your AWS keys info (for EC2 architect)
  - Clone file `docker/docker-compose.dev.yml` as `docker/docker-compose.local.yml`, and point its `env_file` to `envs/env.local`
  - Ensure `envs/env.local` file has a defeinition of these env variables:
      - `PROLIFIC_API_KEY`: set it to your Prolific API key
      - `CYPRESS_CACHE_FOLDER`: set it to any writable folder, e.g. `/tmp`

Now we're ready to launch an example task on Prolific platform:

```shell
docker-compose -f docker/docker-compose.local.yml run \
  --build \
  --publish 3001:3000 \
  --rm mephisto_dc \
  python /mephisto/examples/form_composer_demo/run_task_dynamic_ec2_prolific.py
```

The other steps are similar to launching on MTurk, just task config file is a bit different.

```yaml
#examples/form_composer_demo/hydra_configs/conf/my_config.yaml

#@package _global_
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: ec2  # To launch live, we'll need an external server
  - /mephisto/provider: prolific  # And an external provider

mephisto:
  architect:
    _architect_type: ec2
    profile_name: my_ec2_user  # Name of EC2 user
    subdomain: "0123"  # Each Task Run must have a new subdomain
  blueprint:
    data_json: ${task_dir}/data/dynamic/task_data.json
    task_source: ${task_dir}/webapp/build/bundle.js
    task_source_review: ${task_dir}/webapp/build/bundle.review.js
    link_task_source: false
    extra_source_dir: ${task_dir}/webapp/src/static
    units_per_assignment: 1
  log_level: "debug"
  task:
    task_name: "Sample Questionnaire"
    # Note: don't use `Prolific` in task names, because Prolific will (silently) block your account
    task_title: "Dynamic form-based Tasks for Prolifik"
    task_description: "In this Task, we use dynamic FormComposer feature."
    task_reward: 70
    task_tags: "test,simple,form"
    force_rebuild: true
    max_num_concurrent_units: 1
  provider:
    # Prolific researcher has Workspaces to group Projects
    prolific_workspace_name: "My Workspace"
    # Prolific researcher has Projects to group Studies
    prolific_project_name: "Project"
    # Temporary Prolific Participant Group where we save known workers
    # who satisfy Mephisto qualifications required in this Task
    prolific_allow_list_group_name: "Allow list"
    # Temporary Prolific Participant Group where we save known workers
    # that we have banned during previous task reviews
    prolific_block_list_group_name: "Block list"
    # We can additionally use worker filtering criteria that Prolific platform supprts
    prolific_eligibility_requirements:
      - name: "CustomWhitelistEligibilityRequirement"
        # This limits your Task only to Prolific Participants (workers) with these IDs
        white_list:
          - 6528ff4ac201b9605db841e4
          - 6528ff6b4a6e8ccb70226c4b
          - 6528ff850867369791a99491
          - 6528ffa32c90c600f42b3589
          - 6528ffc2618c084ccb2b37a0
          - 6528ffe199313384fde5028e
          - 652907b023fbe4ed22234d75
          - 652907fb98474afcbe5cb5cd
        # This limits your Task only to Prolific Participants (workers) in this age range
      - name: "ApprovalRateEligibilityRequirement"
        minimum_approval_rate: 1
        maximum_approval_rate: 100
```

For more details, see [Prolific overview](/docs/guides/how_to_use/providers/prolific/intro/).


## 3. Create your own Task

In the introductory examples we user pre-created Tasks. To design your own custom Tasks, you have two options:

- Code your own Task application (build components like React-based UI, custom Agent state, etc). This works best for highly customized Task logic.
  - Examples of custom Tasks include `examples/remote_procedure` and `examples/parlai_chat_task_demo`
- Use an existing Task generator (and specify your task via configs with little, if any, custom coding required). This works best for fairly standard Task logic.
  - form-based Tasks: see [Run FormComposer tasks](/docs/guides/how_to_use/form_composer/running/)
