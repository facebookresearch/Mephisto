# 10-minute Quickstart

First, clone this repo to your local system.

Mephisto requires >= Python 3.6 and >= npm v6.

### Installation

Run the following in the root repo directory:

```bash
$ pip install -e .
```

*Alternatively, we also support installation via the dependency/environment manager project [poetry](https://github.com/python-poetry/poetry) as an option:*

```bash
# install poetry
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
# from the root dir, install Mephisto:
$ poetry install
```

*Are you a Docker user? We support that too! Check out [our Docker guide](docker.md).*

### Setup

Now that you have Mephisto installed, you should have access to the `mephisto` CLI tool.

Let's use this CLI tool to set up a data directory via the `mephisto config` command. The data directory is where the results of your crowdsourcing tasks will be stored.

```bash
$ mephisto config core.mephisto_data_directory ~/mephisto/data
```

Check that everything is set up correctly!
```bash
$ mephisto check
Mephisto seems to be set up correctly.
```

## Step 1. Run your first task (locally)

```bash
$ cd examples/simple_static_task
$ python static_test_script.py
```

This will launch a local HTTP server with the task hosted.
You can then navigate to the task in your browser to complete the task.

To view an instance of a task, look for a print log such as this:

```
[2020-10-30 10:55:26,719][mephisto.providers.mock.mock_unit][INFO] - Mock task launched: l
ocalhost:3000 for preview, localhost:3000/?worker_id=x&assignment_id=20 for assignment 10
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
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

2. Next, let's run the task script again, but this time we'll override the requester name and change the architect type to use [Heroku](https://www.heroku.com/). (You can find all of the architects currently supported [here](../mephisto/abstractions/architects).)

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
