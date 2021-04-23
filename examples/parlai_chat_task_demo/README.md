# ParlAI Chat Task

This task exists to demonstrate both the out-of-the-box functionality of setting up a ParlAI chat on Mephisto, as well as more complicated tasks with custom frontend functionality. To get started you can run one of the following commands:

The baseline chat example can be run from this directory with:
```console
python parlai_test_script.py
```

You can also run an example that has onboarding set up with:
```console
python parlai_test_script.py conf=onboarding_example
```
Which is mostly a wrapper around adding an onboarding qualification, which you can do manually for any of the other configurations.
```console
python parlai_test_script.py conf=... mephisto.blueprint.onboarding_qualification=test_onboard_qualification
```

Further, you can try running a task using a prebuilt customized frontend bundle (built from the `webapp` directory) with:
```console
python parlai_test_script.py conf=custom_prebuilt
```

Further, you can try running a task using an auto-building task (built from the `custom_simple` directory) with:
```console
python parlai_test_script.py conf=custom_simple
```

### Common ParlAI blueprint argument overrides
- `mephisto.blueprint.onboarding_qualification=` (str): Setting this variable enables onboarding (and will grant/ the named qualification from first time workers), which can be used to demo how onboarding worlds and the surrounding functionality works.
- `mephisto.blueprint.custom_source_dir=` (str): Path to the directory to point `ParlAIChatTaskBuilder` to build a custom frontend source from. See usage of `custom_source_dir` in the Task Arguments section to use this for your task.
- `mephisto.blueprint.custom_source_bundle=` (str): Whether or not to launch the task with a prebuilt frontend source file (not created with the `TaskBuilder`) at the provided location.
- `turn_timeout=` (int): Maximum time in seconds to wait for a response between turns before marking a worker as timed out (default 300 seconds).

## Implementation
### Configuration
his task is configured using [Hydra](https://hydra.cc/) - details about using hydra to configure tasks can be read here and in other examples. For more about being able to customize the configuration files, please refer to the [Hydra documentation](https://hydra.cc/docs/intro). Under our current setup, using Hydra means that you must be in the same directory as the python script for hydra to correctly pick up the config files.

### The worlds file
The chats in this example rely on the worlds files in `demo_worlds.py`. The worlds in this file get initialized with agents provided by Mephisto, and then during the chat procedure, data is saved locally to the Mephisto data directory.

Task worlds implement the following methods:
- `parley` - The `parley` method holds the core logic for your world, where ParlAI Agents will interact with one another with `act`s and `observe`s. 
- `episode_done` - The `episode_done` method should return `True` when the conversational episode is over.
- `shutdown` - The `shutdown` method is used to clean up any resources that were allocated upon starting the world, and is called when the episode completes.
- `prep_save_data` (optional) - The `prep_save_data` method is used to add any additional values to the saved conversation data. This data will be accessible later in review.

The world file also needs to implement the following methods:
- `make_world` - This method should, given world options and a list of agents, return an initialized task world. It may optionally accept an `initialization_data` keyword argument, which will be provided with the `Assignment`'s `InitializationData` if present.
- `get_world_params` - This method is used to configure details about your ParlAI world for Mephisto to understand how to initialize your world. In this case the only required configuration parameter is `agent_count`, which specifies the number of human agents Mephisto will provide to your `make_world` function.
- `make_onboarding_world` (optional) - The `make_onboarding_world` method is called to initialize a world on the very first time a specific worker works on your task. This will only ever be called with a single agent, and it should return the initialized onboarding world.
- `validate_onboarding` (optional) - When an onboarding world completes, this method is called on the full data collected in the onboarding task. If it returns `True` the worker is allowed to move on to the full task. If this method returns `False`, then the worker is blocked from working on this task in the future.

### Task arguments (in the run file)
ParlAI chat tasks have a number of arguments set up, primarily via Hydra but also using the `SharedParlAITaskState` object. Details of this are listed below
#### Mephisto required arguments
- `mephisto.task.task_title` - The title of the task showed to workers in their queue
- `mephisto.task.task_description` - The short description for the task that may be showed inline while they're searching for tasks
- `mephisto.task.task_tags` - Any searchable tags that would make it easy to find your task
- `mephisto.task.task_reward` - The reward paid out in dollars for completing your task
- `mephisto.task.task_name` - This task name will be used to consolidate your data across runs. Generally we suggest using `descriptive-string-pilot-#` when piloting and `descriptive-task-string` for your main collection. More details on this are in the (TODO) Mephisto argument instructions.
- `mephisto.blueprint.onboarding_qualification` (optional) - The qualification to grant to a worker when they have completed onboarding, such that they no longer need to do onboarding in future tasks where you specify the same qualification name. Specifying this qualification will make mephisto attempt to run onboarding for new workers, and ommitting it will skip onboarding for all workers.
#### ParlAI-specific arguments
- `mephisto.blueprint.world_file` - Optional path to the python file containing your worlds. Detailed requirements of this file in the "The worlds file" section. If you already know what world module you intend to use for a specific run, it's generally a better practice to import that module directly in your run script, and then pass it as `SharedParlAITaskState.world_module`.
- `mephisto.blueprint.task_description_file` - Path to an HTML file containing the task preview and basic instructions for your task. If you use a custom built frontend, you can omit this argument and directly edit the `TaskPreviewView` in `app.jsx` instead. 
- `mephisto.blueprint.num_conversations` - Number of conversations to have. This currently leads to `num_conversations` * `agent_count` tasks being launched for workers to do. Incomplete tasks are _currently_ not relaunched.
- `mephisto.blueprint.custom_source_dir` - Path to a folder containing, at the very least, a `main.js` for a custom ParlAI frontend view. Can also contain an updated `package.json` if that file imports anything outside of the defaults used in `server/blueprints/parlai_chat/webapp/package.json`. Providing this flag will make Mephisto build that frontend in a `_generated` directory, and refer to that build when launching your task. Mephisto will only rebuild when the source files in the provided `custom_source_dir` are updated.
- `mephisto.blueprint.custom_source_bundle` - Path to a custom built source bundle to deploy to the frontend instead of the standard ParlAI view. For this task we specify a build in the `webapp` directory, but you'll need to run `npm install; npm run dev` in that directory the first time you use a bundle (and whenever you make changes to the `src` that you want to be picked up)
- `SharedParlAITaskState.world_module` - The world file module that you want to provide for this run.
- `SharedParlAITaskState.world_opt` - The world option will be passed to the `make_world` function as the first argument. Passing contents through `world_opt` is the preferred way to share important state between different calls to `make_world`, as this dict will be shared amongst all calls.
- `SharedParlAITaskState.onboarding_world_opt` - The world option will be passed to the `make_onboarding_world` function as the first argument. 

### Task description content
For simple tasks, you can provide an HTML task description (via the `task_description_file` argument above) containing a preview and description of what the worker is going to be doing in their task.

### Simple custom frontend bundles
Using the `mephisto.blueprint.custom_source_dir` option, it's possible to specify just a directory containing any frontend code you are using for a task, so long as you've built the app contained using the `bootstrap-chat` package. In this case, Mephisto will handle the process of generating the bundle whenever it detects changed files, meaning that you don't have to think about that part of the process.

The automated build process looks for three special paths:
- `[custom_source_dir]/main.js` : this should contain your main application code, and is the only required file in the custom source directory. It should probably end with `ReactDOM.render(<MainApp />, document.getElementById("app"));`
- `[custom_source_dir]/style.css` : this can contain any style files that alter the way that your chat application looks. You can later reference this file by including `import "./style.css";` in your `main.js` file.
- `[custom_source_dir]/components/`: This is a special directory that can contain additional elements that your `main.js` file references (using relative paths)
- `[custom_source_dir]/package.json`: If you want additional dependencies, you can specify them in a `package.json` file. We suggest copying the one present at `mephisto/abstractions/blueprints/parlai_chat/webapp/package.json`.

### Custom frontend bundles
Custom frontend bundles can be provided that override the view of how the ParlAI chat looks, and the kinds of inputs you can pass. Most of the ParlAI-specific interfaceing logic is built into the `bootstrap-chat` package. The remaining custom view logic is in `webapp/src/main.js`. Here we define the `RenderChatMessage` component, which overrides the base behavior. 


# How can I make my own task?
## Simple chat collection (no custom frontend) 
If you are able to provide your workers enough context just using a task description and perhaps a message in the chat thread with directions, you should be able to work on a task without a custom frontend. In order to get started on a task like this, you'll likely do the following:

1. Copy the `demo_worlds.py`, `parlai_test_script.py`, and `task_description.html` files to a new directory for your task. This generally would go in the project directory you are launching tasks for, but you can use `mephisto/tasks` if you're just experimenting.  
2. Update any task-related variables in your `conf/my_new_config.yaml` file to make sense for your task.
3. Update your worlds file to specify the kind of conversation you are creating between agents.
4. Run `parlai_test_script.py` to pilot your task over localhost. You can use different `worker_id` URL parameters in different windows to play the part of multiple workers at the same time.
5. Repeat 3 & 4 until you're happy with your task.
6. Launch a small batch on a crowd provider to see how real workers handle your task.
7. Iterate more - use a review script (like the one present in `examples/simple_static_task/examine_results`) to make it easy to see what data you're getting.
8. Collect some interesting conversational data.


## Tasks with custom frontends
If your task needs additional input beyond simple forms (tutorial TODO, see the `respond_with_form` field in the `demo_worlds.py` file in this example to attempt), you'll likely need to be writing your own frontend components. In order to get started on this path, you'll likely do the following:

1. Copy this whole example directory into a new directory for your task. This generally would go in the project directory you are launching tasks for, but you can use `mephisto/tasks` if you're just experimenting.  
2. Update the task-related variables in your `conf/my_new_config.yaml` file to make sense for your task.
3. Update your worlds file to specify the kind of conversation you are creating between agents.
4. Update `app.jsx` to alter parts of your frontend job to do what you want.
5. Rebuild your frontend with `npm install; npm run dev`
6. Run `parlai_test_script.py` to pilot your task over localhost. You can use different `worker_id` URL parameters in different windows to play the part of multiple workers at the same time.
7. Repeat 3 - 6 until you're happy with your task.
8. Launch a small batch on a crowd provider to see how real workers handle your task.
9. Iterate more - use a review script (like the one present in `examples/simple_static_task/examine_results`) to make it easy to see what data you're getting.
10. Collect some interesting conversational data.

You may also find success using the options for the simple custom frontend functionality, described in the "Simple custom frontend bundles" section.

If you do require frontend customization, we recommend using [React Dev Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi?hl=en) to inspect the specific elements you want to change and debug your frontend as you work with it. Note that after rebuilding your frontend (by using `npm install; npm run dev`) you may need to do a force refresh (shift-cmd-R in chrome) to ensure you load the new version of your bundle.
