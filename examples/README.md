<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# Examples
The Mephisto example folders within contain some sample starter code and tasks to demonstrate potential workflows for setting up and working on new tasks.

Mephisto Tasks can be launched (each run is called TaskRun) with a single `docker-compose` command (you will need to have Docker [installed](https://docs.docker.com/engine/install/).)

Let's launch Mephisto example tasks, starting from the easiest one

---

#### 1. Simple HTML-based task

A simple project with HTML-based UI task template [simple_static_task](/examples/simple_static_task)

- Default config file: [/examples/simple_static_task/hydra_configs/conf/example.yaml]
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/simple_static_task/static_test_script.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1)
- Browser page should display an image, instruction, select and file inputs, and a submit button.

---

#### 2. Simple React-based task

A simple project with React-based UI task template [static_react_task](/examples/static_react_task)

- Default config file: [example.yaml](/examples/static_react_task/hydra_configs/conf/example.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/static_react_task/run_task.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1).
- Browser page should display an instruction line and two buttons (green and red).

---

#### 3. Task with dynamic input

A more complex example featuring worker-generated dynamic input: [mnist](/examples/remote_procedure/mnist).

- Default config file: [launch_with_local.yaml](/examples/remote_procedure/mnist/hydra_configs/conf/launch_with_local.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      apt install curl && \
      pip install grafana torch pillow numpy && \
      mephisto metrics install && \
      python /mephisto/examples/remote_procedure/mnist/run_task.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1).
- Browser page should display instructions and a layout with 3 rectangle fields for drawing numbers with a mouse, each field having inputs at the bottom.

---

#### 3. Dynamic form-based task

You can create and modify auto composing forms that we use in command `mephisto form_composer` ([README](/mephisto/generators/form_composer/README.md)) if it looks too easy for you. 

There are three examples:

1. Simple example with already prepared task data config. Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task.py
  ```

2. Dynamic example with already prepared all configs which you can play, regenerate them and see how easy you can make your own more complicated form. Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_dynamic.py
  ```
Also, there are other dynamic commands to play with Prolific or MTurk, just change script name in command to `run_task_dynamic_ec2_prolific.py` and `run_task_dynamic_ec2_mturk_sandbox.py` accordingly.

3. Dynamic example with already prepared all configs, but to show how to work with presigned S3 URLs. 
To make this example fully workable, you need to set AWS credentials as environment variables 
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `S3_URL_EXPIRATION_MINUTES` (if you want to change default 1 hour) in file `docker/envs/env.dev`.
Also, you need to change fake URLs in all configs on private ones from your own S3 storage. 
Or you can use commands to recreate all configs aotomatically. Read how to do this [here](/mephisto/generators/form_composer/README.md#using-formcomposerconfig-utility).
Example of `form_composer_config` command will be:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      mephisto form_composer_config --update-file-location-values "https://s3.amazon.com/...." --use_presigned_urls
  ```
After you generetad/changed all configs, you can launch with next command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_dynamic_presigned_urls.py
  ```

---

# Your Mephisto project

To read on steps for creating your own custom Mephisto task, please refer to README in the main Mephisto repo.
