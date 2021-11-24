---
sidebar_position: 2
---

# Working on a custom task

Now that you've [launched a task or two](first_task), it's time to get into building your own. This tutorial focuses on giving you the tools to collect the specific data you're looking for by building a task of your own. This tutorial itself won't produce a useful task, but it should be useful for understanding how to go about creating a real one. You don't need any React experience to get through this guide, though it will be helpful for understanding the usage more deeply.

## 1. Getting started
### 1.1 Making a new workspace
We'll extend from the static react task example, but we'll want to move it to it's own workspace. From within the main Mephisto directory:
```bash
cp -r examples/static_react_task/ tmp/static_tutorial/
cd tmp/static_tutorial/
```

Now that we're here, we should also set up your config file
```yaml
# hydra_configs/conf/example.yaml 
#@package _global_
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
mephisto:
  blueprint:
    task_source: ${task_dir}/webapp/build/bundle.js
    link_task_source: false
    extra_source_dir: ${task_dir}/webapp/src/static
    units_per_assignment: 1
  task:
    task_name: custom-react-tutorial   # Remember to set an appropriate task_name!
    task_title: "Rating a sentence as good or bad"
    task_description: "In this task, you'll be given a sentence. It is your job to rate it as either good or bad."
    task_reward: 0.05
    task_tags: "test,simple,button"
```

The only change we'll make is to the `task_name` (as you should on any new tasks!), but we will update the other fields as we go. It's important to note the `task_source` and `extra_source_dir` arguments though, as this is where the `Blueprint` will be looking a compiled react app bundle, and for extra static resources for the page.

### 1.2 Launching the task
From the current directory, you should be able to execute the run script and get a job working. We're using a different `task_name` to prevent polluting our later task with data that won't share the same format. It is a good practice to do this with initial iterations, and to change the `task_name` any time you change input or output arguments.
```bash
python run_task.py mephisto.task.task_name=custom-react-tutorial-iterating
```
This will launch a simple task where an annotator is supposed to note a sentence as being good or bad. Clicking a button auto-submits the task. In the next sections we'll add other content. 

Moving forward, we'll update this task so that workers are able to edit the text as well as rate the original sentence.

## 2. Providing new data to the task
### 2.1 The `SharedTaskState` object and `static_task_data` attribute
We'll begin by modifying the `SharedStaticTaskState`'s `static_task_data` attribute. For info on this attribute, recall `mephisto wut`:
```bash 
$ mephisto wut blueprint=static_react_task static_task_data

                Tasks launched from static blueprints need
                a prebuilt javascript bundle containing the task. We suggest building
                with our provided useMephistoTask hook.
            

Additional SharedTaskState args from SharedStaticTaskState, which may be configured in your run script
dest              type                      default    help                                     choices    required
----------------  ------------------------  ---------  ---------------------------------------  ---------  ----------
static_task_data  Iterable[Dict[str, Any]]  []         List or generator that returns dicts of  None       False
                                                       task data. Generators can be used for
                                                       tasks with lengths that aren't known at
                                                       the start of a run, or are otherwise
                                                       determined during the run.
```
This field replaces using the `csv_file` used in the previous tutorial, allowing our run script to specify data directly. React tasks can be run off of `.csv` files as well, if you'd prefer.

At the moment, the data we're providing is as follows:
```python
shared_state = SharedStaticTaskState(
    static_task_data=[
        {"text": "This text is good text!"},
        {"text": "This text is bad text!"},
    ],
    ...
)
```
This corresponds to two `Assignment`s, each with an entry for `text`. Altering these will change the text that is present, while adding new entries to the array will lead to Mephisto generating more `Assignment`s. 

### 2.2 Editing `static_task_data`

For now let's just edit the data and add a new field. Update the `static_task_data` to look like this:
```python
static_task_data=[
    {"text": "I have edited this text! Now it is extra good", "edited_by_requester": True},
    {"text": "This text is bad text!", "edited_by_requester": False},
],
```

At this point you can run the task again.
```bash
python run_task.py mephisto.task.task_name=custom-react-tutorial-iterating
```
Note the first one you work on displays your new edited text. But what about the new `edited` field?

> **Tip:** In your own tasks, you can use a function that creates static task data, or even a generator for it, but this is discussed more in the [workflows](workflows) tutorial.

## 3. Accessing the new data
### 3.1 Using React Dev Tools
TODO - Show the user how to install react dev tools, then direct them to be able to see the field in a running task

### 3.2 Making a component to render the new data
TODO - Create a component that says whether or not the sentence was edited.

### 3.3 Adding a component to respond with new data
TODO - update the send part, such that you now send the data of the edited text when rated `bad`.

## 4. Setting up a review
### 4.1 Examining the raw data

TODO - show creating a review script for the raw data
### 4.2 Creating a viewer

TODO - write an actual viewer.

# Pointer to @Annotated

TODO - quick note to check out annotated storybook for design ideas and components to use