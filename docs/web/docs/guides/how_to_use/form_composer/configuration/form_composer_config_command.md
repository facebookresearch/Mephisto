---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 3
---

# `form_composer config` command

The `form_composer config` utility command helps auto-generate FormComposer config. It supports several options:

```shell
# Sample launching commands
mephisto form_composer config
mephisto form_composer config --update-file-location-values "https://s3.amazonaws.com/..." --use_presigned_urls
mephisto form_composer config --update-file-location-values "https://s3.amazonaws.com/..."
mephisto form_composer config --permutate-separate-tokens
mephisto form_composer config --extrapolate-token-sets
mephisto form_composer config --verify
# Parameters that work together
mephisto form_composer config --directory /my/own/path/to/data/ --verify
mephisto form_composer config --directory /my/own/path/to/data/ --extrapolate-token-sets
mephisto form_composer config --update-file-location-values "https://s3.amazonaws.com/..."
```

where
- `-d/--directory` - a **modifier** for all `form_composer config` command options that specifies the directory where all form JSON config files are located (if missing the default is `mephisto/generators/form_composer/data` directory)
- `-v/--verify` - if truthy, validates all JSON configs currently present in the form builder config directory
- `-p/--permutate-sepatate-tokens` - if truthy, generates token sets values as all possible combinations of values of individual tokens
- `-f/--update-file-location-values S3_FOLDER_URL` - generates token values based on file names found within the specified S3 folder (see a separate section about this mode of running FormComposer)
- `-e/--extrapolate-token-sets` - if truthy, generates Task data config based on provided form config and takon sets values
- `-u/--use-presigned-urls` - a **modifier** for `--update-file-location-values` command that converts S3 URLs into short-lived rtemporary ones (for more detailes see "Presigned URLs" section)

## Shortcut commands

- `mephisto form_composer config` executes the following commands in one step:
```shell
mephisto form_composer config --permutate-separate-tokens
mephisto form_composer config --extrapolate-token-sets
mephisto form_composer config --verify
```
