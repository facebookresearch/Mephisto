---
sidebar_position: 1
---

# How task run works

Let's understand basic components of the task launch, such as configs and the `run_task.py` script. This will help with customization of tash launch behaviors.

### 3.1 Config registration

Mephisto wires up to configuration using standard Hydra syntax, but with both `yaml` files (for ease of writing) _and_ structured configs (for ease of documentation).
Here's the config we've set up for this example:

```python
# examples/form_composer_demo/run_task.py
import os

from omegaconf import DictConfig

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import build_custom_bundle
from mephisto.tools.scripts import task_script


@task_script(default_config_file="example_local_mock")
def main(operator: Operator, cfg: DictConfig) -> None:
```

This is all you really *need* to launch a Mephisto task! The `@task_script` decorator does the job of attaching your hydra yaml as default arguments for the main.

Of course, there's quite a bit of 'magic' happening underneath the hood thanks to the script utilities.
This version is explicit to show where you may add customization, and re-ordered for understanding:
```python
# modified examples/form_composer_demo/run_task.py
import os
from dataclasses import dataclass
from typing import Any

from omegaconf import DictConfig

from mephisto.operations.operator import Operator
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.tools.scripts import build_custom_bundle
from mephisto.tools.scripts import task_script

@dataclass
class MyTaskConfig(build_default_task_config('example_local_mock')):
    custom_args: Any = 4

@task_script(config=MyTaskConfig)
def main(operator: Operator, cfg: DictConfig) -> None:
```

In this snippet, we do a few things:
1. We set up the default [`conf`](https://hydra.cc/docs/tutorials/basic/your_first_app/config_file/) file to be `example_local_mock`,
using `build_default_task_config`, which returns a `TaskConfig` that we can extend.
2. We extend the returned `TaskConfig` with `MyTaskConfig`, which allows us to specify custom arguments.
3. We decorate the main, noting that the correct config is `MyTaskConfig`.
Note that the `default_config_file` version of this simply takes care of the above steps inline in the decorator.

With all the above, we're able to just make edits to `example_local_mock.yaml` or make other configs in the `conf/` directory and route to them directly.

### 3.2 Invoking Mephisto

Mephisto itself is actually invoked just a little later:

```python
@task_script(default_config_file="example_local_mock")
def main(operator: Operator, cfg: DictConfig) -> None:
    # Build packages
    _build_custom_bundles(cfg)

    operator.launch_task_run(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)
```

Under the hood the `task_script` decorator extracts specific arguments out of your configuration
(and surface warnings about incompatibilities) and initializes an `Operator` on the correct `MephistoDB` for the task.
Using this we can launch a `TaskRun` the given config, then wait for it to run.
To ensure we're not frozen, the operator takes in a `log_rate` in seconds to print status messages while the run is underway.

### 3.3 Default abstraction usage

Again we can look back at the `example_local_mock.yaml` file to see this setup:

```yaml
# examples/form_composer_demo/hydra_configs/conf/example_local_mock.yaml
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
```

These ensure that, when not provided other arguments, we launch this task locally using a `LocalArchitect` and `MockProvider`.
With these defaults, this and other example tasks are run using a "local" architect, and a "mock" requester without arguments.
The "local" architect is reponsible for running a server on your local machine to host the task,
and the "mock" requester lets *you* simulate a worker without using an external crowd-provider platform such as Prolific or MTurk to launch the task.

### 3.4 `Unit` creation explained

When stepping through this task the first time, you ended up working on two `Unit`s as two different `Worker`s.
It's useful to understand how this happens.
Taking a look at the config and data:

```yaml
# examples/form_composer_demo/hydra_configs/conf/example_local_mock.yaml

#@package _global_
defaults:
...
mephisto:
  ...
  blueprint:
    data_json: ${task_dir}/data/simple/task_data.json
    ...
    units_per_assignment: 1
  task:
    ...
```

```json
// examples/form_composer_demo/data/simple/task_data.json

[
  {
    "form": {
      "title": "Form example",
      "instruction": "Please answer all questions to the best of your ability as part of our study.",
      "sections": [
        {
          "name": "section_about",
          "title": "About you",
          "instruction": "Please introduce yourself. We would like to know more about your background, personal information, etc.",
          "fieldsets": [
            {
              "title": "Personal information",
              "instruction": "",
              "rows": [
                {
                  "fields": [
                    {
                      "help": "",
                      "id": "id_name_first",
                      "label": "First name",
                      "name": "name_first",
                      "placeholder": "Type first name",
                      "tooltip": "Your first name",
                      "type": "input",
                      "validators": {
                        "required": true,
                        "minLength": 2,
                        "maxLength": 20
                      },
                      "value": ""
                    },
                    {
                      "help": "Optional",
                      "id": "id_name_last",
                      "label": "Last name",
                      "name": "name_last",
                      "placeholder": "Type last name",
                      "tooltip": "Your last name",
                      "type": "input",
                      "validators": { "required": true },
                      "value": ""
                    }
                  ],
                  "help": "Please use your legal name"
                },
                {
                  "fields": [
                    {
                      "help": "We may contact you later for additional information",
                      "id": "id_email",
                      "label": "Email address for Mephisto",
                      "name": "email",
                      "placeholder": "user@mephisto.ai",
                      "tooltip": "Email address for Mephisto",
                      "type": "email",
                      "validators": {
                        "required": true,
                        "regexp": ["^[a-zA-Z0-9._-]+@mephisto\\.ai$", "ig"]
                      },
                      "value": ""
                    }
                  ]
                }
              ]
            },
            {
              "title": "Cultural background",
              "instruction": "Please tell us about your cultural affiliations and values that you use in your daily life.",
              "rows": [
                {
                  "fields": [
                    {
                      "help": "Select country of your residence",
                      "id": "id_country",
                      "label": "Country",
                      "multiple": false,
                      "name": "country",
                      "options": [
                        {
                          "label": "---",
                          "value": ""
                        },
                        {
                          "label": "United States of America",
                          "value": "USA"
                        },
                        {
                          "label": "Canada",
                          "value": "CAN"
                        }
                      ],
                      "placeholder": "",
                      "tooltip": "Country",
                      "type": "select",
                      "validators": { "required": true },
                      "value": ""
                    },
                    {
                      "help": "Select language spoken in your local community",
                      "id": "id_language",
                      "label": "Language",
                      "multiple": true,
                      "name": "language",
                      "options": [
                        {
                          "label": "English",
                          "value": "en"
                        },
                        {
                          "label": "French",
                          "value": "fr"
                        },
                        {
                          "label": "Spanish",
                          "value": "es"
                        },
                        {
                          "label": "Chinese",
                          "value": "ch"
                        }
                      ],
                      "placeholder": "",
                      "tooltip": "Language",
                      "type": "select",
                      "validators": {
                        "required": true,
                        "minLength": 2,
                        "maxLength": 3
                      },
                      "value": ""
                    }
                  ]
                }
              ],
              "help": "This information will help us compile study statistics"
            },
            {
              "title": "Additional information",
              "instruction": "Optional details about you. You can fill out what you are most comfortable with.",
              "rows": [
                {
                  "fields": [
                    {
                      "help": "",
                      "id": "id_bio",
                      "label": "Biography since age of 18",
                      "name": "bio",
                      "placeholder": "",
                      "tooltip": "Your bio in a few paragraphs",
                      "type": "textarea",
                      "validators": { "required": false },
                      "value": ""
                    }
                  ]
                },
                {
                  "fields": [
                    {
                      "help": "",
                      "id": "id_skills",
                      "label": "Technical Skills",
                      "name": "skills",
                      "options": [
                        {
                          "checked": false,
                          "label": "React",
                          "value": "react"
                        },
                        {
                          "checked": true,
                          "label": "JavaScript",
                          "value": "javascript"
                        },
                        {
                          "checked": false,
                          "label": "Python",
                          "value": "python"
                        },
                        {
                          "checked": false,
                          "label": "SQL",
                          "value": "sql"
                        }
                      ],
                      "tooltip": "Technical skills you may possess",
                      "type": "checkbox",
                      "validators": {
                        "required": true,
                        "minLength": 2,
                        "maxLength": 3
                      }
                    }
                  ]
                },
                {
                  "fields": [
                    {
                      "help": "",
                      "id": "id_kids",
                      "label": "How many children do you have?",
                      "name": "kids",
                      "options": [
                        {
                          "checked": false,
                          "label": "None",
                          "value": "0"
                        },
                        {
                          "checked": false,
                          "label": "One",
                          "value": "1"
                        },
                        {
                          "checked": false,
                          "label": "Two",
                          "value": "2"
                        },
                        {
                          "checked": false,
                          "label": "Three or more",
                          "value": ">=3"
                        }
                      ],
                      "tooltip": "How many children do you have?",
                      "type": "radio",
                      "validators": { "required": true }
                    }
                  ]
                },
                {
                  "fields": [
                    {
                      "help": "",
                      "id": "id_avatar",
                      "label": "Profile Picture",
                      "name": "avatar",
                      "placeholder": "Select a file",
                      "tooltip": "Your profile photo",
                      "type": "file",
                      "validators": { "required": true },
                      "value": ""
                    },
                    {
                      "help": "",
                      "id": "id_resume",
                      "label": "Resume",
                      "name": "resume",
                      "placeholder": "Select a file",
                      "tooltip": "Your current resume",
                      "type": "file",
                      "validators": { "required": false },
                      "value": ""
                    }
                  ]
                }
              ],
              "help": "Some additional details about your persona"
            }
          ]
        },
        {
          "name": "section_second",
          "title": "Second section",
          "instruction": "Example of another section",
          "fieldsets": [
            {
              "title": "Motivation",
              "instruction": "",
              "rows": [
                {
                  "fields": [
                    {
                      "help": "",
                      "id": "id_motto",
                      "label": "Personal Motto",
                      "name": "motto",
                      "placeholder": "",
                      "tooltip": "Your personal motto",
                      "type": "input",
                      "validators": { "required": true },
                      "value": ""
                    }
                  ],
                  "help": "Please type in your favorite personal motto"
                }
              ]
            }
          ]
        }
      ],
      "submit_button": {
        "text": "Submit",
        "tooltip": "Submit form"
      }
    }
  }
]

```

From this, we know we're loading from `task_data.json`, and that this file only has one listed item.
Mephisto creates an `Assignment` for each of these lines, representing a group of work for which a worker can only contribute to once.
We also specify two `units_per_assignment`, meaning that Mephisto creates one `Unit`s per `Assignment`,
meaning in this case that different workers can complete the same job, usually to get inter-annotator agreement.
(In some cases Mephisto can use an `Assignment` to connect multiple workers each with one `Unit` on a collaborative live task).
As we had one assignment, it makes sense that each worker `x` and your second worker could only complete one task each.
