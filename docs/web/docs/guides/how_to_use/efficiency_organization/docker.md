<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# Running Mephisto with Docker

You may want to keep Mephisto environment entirely contained, and set it up with just a few commands. To do this, we support Docker and Docker Compose as a launch option.

## Installation

Install Docker and Docker Compose using the [official guide](https://docs.docker.com/get-docker/). You can learn about Docker Compose commands on its [documentation page](https://docs.docker.com/compose/).

## Running form-based task example

```shell
docker-compose -f docker/docker-compose.dev.yml run \
  --build \
  --publish 3001:3000 \
  --rm mephisto_dc \
  python /mephisto/examples/form_composer_demo/run_task.py
```

## Customizing Docker settings

All docker settings you can find in [`docker` directory](https://github.com/facebookresearch/Mephisto/tree/main/docker).

Files and directories:
- `docker-compose.dev.yml` - minimal development Docker Compose config to start all our examples and apps
- `docker-compose.dev.vscode.yml` - same as previous, but set up with Python-debugger for VS Code as it requires extra settings
- `aws_credentials.example` - example of the structure of file `aws_credentials`; this file is mounted into `~/.aws/credentials` file inside dockerized environment
- `entrypoints` - directory with entrypoint scripts (used to run commands at launching of a Docker container)
  - `server.mturk.sh` - example for MTurk
  - `server.prolific.sh` - example for Prolific
- `envs` - directory with environmental variales for the dockerized environment
  - `env.dev` - lists env variables you may need for Mephisto (populate these empty values according to your needs)

If you want to customize Docker configs (e.g. use your AWS credentials), we recommend you to create these files, and save your customizations in them:
- `server.local.sh` in entrypoints
- `env.local` in `envs`
- `docker-compose.local.yml` config next to the standard `docker-compose.dev.yml` (and point it to `server.local.sh` and `env.local` files)

Now you can enable your Docker customizations simply by specifying `-f docker/docker-compose.local.yml` parameter in all Docker Compose commands. For example:
```shell
docker-compose -f docker/docker-compose.local.yml run \
  --build \
  --publish 3001:3000 \
  --rm mephisto_dc \
  python /mephisto/examples/form_composer_demo/run_task.py
```
