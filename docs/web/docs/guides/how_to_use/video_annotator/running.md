---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# Run VideoAnnotator tasks

To create and launch a VideoAnnotator task, first create your JSON form configuration,
and then run the below commands.

Once your Task launches, your console will display you URLs like this: `http://<YOUR_DOMAIN>/?worker_id=x&assignment_id=1`.

- If you're doing local testing with `local` architect and `inhouse` provider, your URLs will start with `http://localhost:3000/`. To access your Task units as a worker, just paste one of these URLs into your browser.
    - _If running with Docker, you will need to replace port `3000` in the console URLs with the remapped port (e.g. for `3001:3000` it will be `3001`)._
- If you're running with a "real" provider, to access your Task units you will need to log into the provider's platform as a worker, and find them there.


#### With docker-compose

You can launch VideoAnnotator inside a Docker container:

1. Prepare configs using [`video_annotator config` command](/docs/guides/how_to_use/video_annotator/configuration/video_annotator_config_command/):

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --rm mephisto_dc \
    mephisto video_annotator config --extrapolate-token-sets
```

2. Run annotator itself using `video_annotator` command:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --publish 3001:3000 \
    --rm mephisto_dc \
    mephisto video_annotator
```

#### Without docker-compose

First ensure that mephisto package is installed locally - please refer to [Mephisto's main doc](https://mephisto.ai/docs/guides/quickstart/).
Once that is done, run [`video_annotator config` command](/docs/guides/how_to_use/video_annotator/configuration/video_annotator_config_command/) if needed, followed by `video_annotator` command:

```shell
# Configure command (for details, see "video_annotator config command" page)
mephisto video_annotator config --extrapolate-token-sets

# Run commands
mephisto video_annotator
mephisto video_annotator --task-data-config-only
mephisto video_annotator --conf my-yaml-config
```

where
- `-o/--task-data-config-only` - validate only final data config
- `-c/--conf` - YAML config name (analog of `conf` option in raw python run script)
