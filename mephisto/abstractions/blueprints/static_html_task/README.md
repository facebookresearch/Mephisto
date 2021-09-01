# `StaticHTMLBlueprint`
## Overview
The `StaticHTMLBlueprint` exists to create a simple transition stand-in to allow users of other platforms (which generally push for customization with HTML) to begin using Mephisto with minimal changes. This generally exists in the form of specifying a templated HTML file and providing assignment data that fills the templates.

There are no plans to extend the `StaticHTMLBlueprint`, or provide other HTML support, as we believe this to be more an onboarding ramp rather than a fully fleshed out feature. The `React`-based codebase contains better features and cleaner, reusable modules, and as such our focus is on tasks in that area.

## Usage
An example usage case is available [here](https://github.com/facebookresearch/Mephisto/blob/main/examples/simple_static_task/). General usage for this `Blueprint` type can be summed up as copying that directory structure, providing your own templated HTML in the `server_files`, and then providng the `data.csv` or other data to post those templates to workers. More in-depth descriptions can be seen there.

## Implementation Details
At a high level, this is a deeper implementation of the abstract `StaticArchitect`, which contains all of the logic for deploying arbitrary tasks where the worker is given some content, and we ask for one response, as a complete `Unit`. This module adds the logic to ensure that the frontend where the worker is given content is able to render arbitrary HTML.
### `app.jsx`
The `app.jsx` file contains most of the logic to ensure we can render HTML, including being able to attach and execute the arbitrary scripts that are included or linked in the given HTML file. It creates a react application using the `mephisto-task` package, and creates an empty form with a submit button. It then populates the inner form using two primary methods:
- `handleUpdatingRemainingScripts`: This method walks through the list of scripts that are given in the attached HTML, either loading the external script and putting it into the head, or directly evaluating the content of local scripts. As the page has already loaded by the time we are loading in the remaining scripts, this all must be injected in an asynchronous manner. _Ultimately_ this isn't incredibly safe if you don't trust the attached scripts.
- `interpolateHtml`: This method injects the values for the specific task into their template variable slots. These template variables are specified in the `InitializationData` for an assignment, and populate fields as noted in the **Template Variables** section below.

Upon submit, the data in the form (as marked by the `name` fields of any inputs) will be sent to the backend and stored in the `agent_data.json` file.

#### Template Variables
You can provide template variables when running your task, generally in the form of template variables that are given names. When you specify these (either via `.csv` or directly providing a parsed array of dicts for this data), any named variable `my_special_variable` will be filled into the frontend in all locations containing `${my_special_variable}`.
#### Mephisto-specific Template Variables
As of now, we also make available the following variables to the HTML via templating:
- `${mephisto_agent_id}`: The agent ID that Mephisto has associated with the current worker and task.
- `${provider_worker_id}`: The worker id that the provider uses locally to identify the worker.

### `StaticHTMLBlueprint`
The `Blueprint` here extends on the abstract `StaticBlueprint`, adding HTML-specific requirements to outline the task that ends up visualized. The added arguments are as follows:
- `task_source`: The path to the (templated) HTML that should be displayed for the task.
- `preview_source`: The path to the HTML that should be displayed while previewing a task.
- `onboarding_source`: The path to the HTML that should be displayed during onboarding.

Providing an `onboarding_source` requires also providing an `onboarding_qualification` in order to trigger onboarding for your task. You should also specify a `validate_onboarding` in your `SharedTaskState` to ensure that the onboarding is completed properly.

### `StaticHTMLTaskBuilder`
This `TaskBuilder` class primarily seeks to copy the source files as linked in the `StaticHTMLBlueprint` and include them in what gets deployed on the server. As these are primarily static files, the builder is fairly straightforward. Regardless of the files that are provided, the onboarding html ends up at `onboarding.html` on the server and the preview html ends up on the server at `preview.html`. The task html retains its name, as this is specified as the `html` arg parsed on the frontend.