---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 4
---

# Embed FormComposer into custom application

A few tips if you wish to embed FormComposer in your custom application:

- To extrapolate form config (and generate the `task_data.json` file), call the extrapolator function `mephisto.generators.form_composer.configs_validation.extrapolated_config.create_extrapolated_config`
    - For a live example, you can explore the source code of [run_task_dynamic.py](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/run_task_dynamic.py) module
- To use code insertions:
    - for custom validators:
        - Point `WEBAPP__FORM_COMPOSER__CUSTOM_VALIDATORS` backend env variable to the location of `custom_validators.js` module (before building all webapp applications)
        - When using `FormComposer` component, import validators with `import * as customValidators from "custom-validators";` and pass them to your `FormComposer` component as an argument: `customValidators={customValidators}`
        - Set this alias in your webpack config (to avoid build-time exception that `custom-validators` cannot be found):
        ```js
        resolve: {
          alias: {
            ...
            "custom-validators": path. resolve(
              process.env.WEBAPP__FORM_COMPOSER__CUSTOM_VALIDATORS
            ),
          },
        }
        ```
    - for custom triggers:
        - Point `WEBAPP__FORM_COMPOSER__CUSTOM_TRIGGERS` backend env variable to the location of `custom_triggers.js` module (before building all webapp applications)
        - When using `FormComposer` component, import triggers with `import * as customTriggers from "custom-triggers";` and pass them to your `FormComposer` component as an argument: `customTriggers={customTriggers}`
        - Set this alias in your webpack config (to avoid build-time exception that `custom-triggers` cannot be found):
        ```js
        resolve: {
          alias: {
            ...
            "custom-triggers": path. resolve(
              process.env.WEBAPP__FORM_COMPOSER__CUSTOM_TRIGGERS
            ),
          },
        }
        ```
