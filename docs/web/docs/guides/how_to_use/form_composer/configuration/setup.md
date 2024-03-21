---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 5
---

# FormComposer configuration

FormComposer tasks are fully defined by their configuration files. These files comprise:
- The main JSON file `task_data.json` that specifies all fields across all form versions (their visual layout, validators, etc)
- Auxiliary JSON files (such as `token_sets_values_config.json`) that specifies certain parts of the main config (e.g. only variable parts varing between form versions). The main JSON file is construvted out of these by using `mephisto form_composer` CLI command.
- Custom pieces of code specified in a special `insertions` subdirectory, such as HTML content of lengthy form instructions.

The structure and purpose of these files is detailed further in other sections:
- [Config files reference](/docs/guides/how_to_use/form_composer/configuration/config_files/)
- [Using multiple form versions](/docs/guides/how_to_use/form_composer/configuration/multiple_form_versions/)
- [form_composer_config command](/docs/guides/how_to_use/form_composer/configuration/form_composer_config_command/)
- [Using code insertions](/docs/guides/how_to_use/form_composer/configuration/insertions/)
- [Form rendering callbacks](/docs/guides/how_to_use/form_composer/configuration/form_callbacks/)


To test the effect of configuration changes on a finished Task, you can use working FormComposer examples in the `examples/form_composer_demo/data` directory.
