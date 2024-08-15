---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# Run FormComposer tasks

To create and launch a FormComposer task, first create your JSON form configuration,
and then run the below commands.

Once your Task launches, your console will display you URLs like this: `http://<YOUR_DOMAIN>/?worker_id=x&assignment_id=1`.

- If you're doing local testing with `local` architect and `mock` provider, your URLs will start with `http://localhost:3000/`. To access your Task units as a worker, just paste one of these URLs into your browser.
    - _If running with Docker, you will need to replace port `3000` in the console URLs with the remapped port (e.g. for `3001:3000` it will be `3001`)._
- If you're running with a "real" provider, to access your Task units you will need to log into the provider's platform as a worker, and find them there.


#### With docker-compose

You can launch FormComposer inside a Docker container:

1. Prepare configs using [`form_composer config` command](/docs/guides/how_to_use/form_composer/configuration/form_composer_config_command/):

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --rm mephisto_dc \
    mephisto form_composer config --extrapolate-token-sets
```

2. Run composer itself using `form_composer` command:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --publish 3001:3000 \
    --rm mephisto_dc \
    mephisto form_composer
```

#### Without docker-compose

First ensure that mephisto package is installed locally - please refer to [Mephisto's main doc](https://mephisto.ai/docs/guides/quickstart/).
Once that is done, run [`form_composer config` command](/docs/guides/how_to_use/form_composer/configuration/form_composer_config_command/) if needed, followed by `form_composer` command:

```shell
# Configure command (for details, see "form_composer config command" page)
mephisto form_composer config --extrapolate-token-sets

# Run commands
mephisto form_composer
mephisto form_composer --task-data-config-only
mephisto form_composer --conf my-yaml-config
```

where
- `-o/--task-data-config-only` - validate only final data config
- `-c/--conf` - YAML config name (analog of `conf` option in raw python run script)
