---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 3
---

# `video_annotator config` command

The `video_annotator config` utility command helps auto-generate VideoAnnotator config. It supports several options:

```shell
# Sample launching commands
mephisto video_annotator config
mephisto video_annotator config --update-file-location-values "https://s3.amazonaws.com/..." --use_presigned_urls
mephisto video_annotator config --update-file-location-values "https://s3.amazonaws.com/..."
mephisto video_annotator config --permutate-separate-tokens
mephisto video_annotator config --extrapolate-token-sets
mephisto video_annotator config --verify
# Parameters that work together
mephisto video_annotator config --directory /my/own/path/to/data/ --verify
mephisto video_annotator config --directory /my/own/path/to/data/ --extrapolate-token-sets
mephisto video_annotator config --update-file-location-values "https://s3.amazonaws.com/..."
```

where
- `-d/--directory` - a **modifier** for all `video_annotator config` command options that specifies the directory where all annotator JSON config files are located (if missing the default is `mephisto/generators/video_annotator/data` directory)
- `-v/--verify` - if truthy, validates all JSON configs currently present in the annotator builder config directory
- `-p/--permutate-sepatate-tokens` - if truthy, generates token sets values as all possible combinations of values of individual tokens
- `-f/--update-file-location-values S3_FOLDER_URL` - generates token values based on file names found within the specified S3 folder (see a separate section about this mode of running VideoAnnotator)
- `-e/--extrapolate-token-sets` - if truthy, generates Task data config based on provided annotator config and token sets values
- `-u/--use-presigned-urls` - a **modifier** for `--update-file-location-values` command that converts S3 URLs into short-lived rtemporary ones (for more detailes see "Presigned URLs" section)

## Shortcut commands

- `mephisto video_annotator config` executes the following commands in one step:
```shell
mephisto video_annotator config --permutate-separate-tokens
mephisto video_annotator config --extrapolate-token-sets
mephisto video_annotator config --verify
```
