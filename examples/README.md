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

You can create and modify auto-composed form-based tasks using FormComposer example (its full specs are in this [README](/mephisto/generators/form_composer/README.md)).

There are three FormComposer examples:

##### 3.1. Simple form

This is a single-version form containing no variable tokens.

- Default config file: [example_local_mock.yaml](/examples/form_composer_demo/hydra_configs/conf/example_local_mock.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1).
- You should see a Bootstrap-themed form with fields and sections corresponding to the form config in its [task_data.json](/examples/form_composer_demo/data/simple/task_data.json) file.

##### 3.2. Simple form with Gold Units

Same example as 3.1, but one of the Units will be marked as Gold.

- Default config file: [example_local_mock.yaml](/examples/form_composer_demo/hydra_configs/conf/example_local_mock_with_gold_unit.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_with_gold_unit.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1).
- You should see a Bootstrap-themed form with fields and sections corresponding to the form config in its [task_data.json](/examples/form_composer_demo/data/simple/task_data.json) file
and Gold units made from [gold_units_data.json](/examples/form_composer_demo/data/simple/gold_units/gold_units_data.json)
with special validation for them from [gold_units_validation.py](/examples/form_composer_demo/data/simple/gold_units/gold_units_validation.py).

##### 3.3. Simple form with Onboarding

Same example as 3.1, but before Units a Worker will see Onboarding widget.

- Default config file: [example_local_mock.yaml](/examples/form_composer_demo/hydra_configs/conf/example_local_mock_with_oboarding.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_with_onboarding.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1).
- You should see Onboarding widget and after answering the onboarding question you will be blocked or passed further and will see
a Bootstrap-themed form with fields and sections corresponding to the form config in its [task_data.json](/examples/form_composer_demo/data/simple/task_data.json) file.

##### 3.4. Simple form with Screening units

Same example as 3.1, but first time before real Units a Worker will see Screening units.

- Default config file: [example_local_mock.yaml](/examples/form_composer_demo/hydra_configs/conf/example_local_mock_with_screening.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_with_screening.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1).
- You should see Onboarding widget and after answering the onboarding question you will be blocked or passed further and will see
a Bootstrap-themed form with fields and sections corresponding to the form config in its [task_data.json](/examples/form_composer_demo/data/simple/task_data.json) file
and Screening units made from [screening_units_data.json](/examples/form_composer_demo/data/simple/screening_units/screening_units_data.json)
with special validation for them from [screening_units_validation.py](/examples/form_composer_demo/data/simple/screening_units/screening_units_validation.py).

##### 3.5. Simple form with Worker Opinion widget

Same example as 3.1, but after completing a Unit, a Worker will see a form below the main form where they can leave their opinion and screenshots.

- Default config file: [example_local_mock.yaml](/examples/form_composer_demo/hydra_configs/conf/example_local_mock_with_oboarding.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_with_worker_opinion.py
  ```
- Browser page (for the first task unit): [http://localhost:3001/?worker_id=x&assignment_id=1](http://localhost:3001/?worker_id=x&assignment_id=1).
- You should see a Bootstrap-themed form with fields and sections corresponding to the form config in its [task_data.json](/examples/form_composer_demo/data/simple/task_data.json) file.

##### 3.6. Dynamic form

Dynamic form means a multi-version form, where versions are generated by varying values of special tokens embedded into the form config.

- Default config file: [dynamic_example_local_mock.yaml](/examples/form_composer_demo/hydra_configs/conf/dynamic_example_local_mock.yaml).
- Launch command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_dynamic.py
  ```
- Browser page is same as for the Simple form example

There are variations of dynamic form config that use different providers. To try that, change `run_task_dynamic.py` in the launch command to:

- `run_task_dynamic_ec2_prolific.py` for Prolific (requires valid EC2 credentials)
- `run_task_dynamic_ec2_mturk_sandbox.py` for Mechanical Turk sandbox (requires valid EC2 credentials)

##### 3.7. Dynamic form with presigned URLs

This example builds further upon the Dynamic form example. Here we use presigned URLs (i.e. short-lived URLs for S3 AWS files) in the displayed forms, for data security.

- Set up environment variables (in file `docker/envs/env.dev`):
    - Required: valid AWS credentials: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`
    - Required: a private S3 bucket with files that you will embed in the example form (either replace dummy URLs in the configs by hand, or automatically generate new ones with `mephisto form_composer config` command)
    - Optional: `S3_URL_EXPIRATION_MINUTES` (default value is 60 minutes)
- Default config file: [dynamic_example_local_mock.yaml](/examples/form_composer_demo/hydra_configs/conf/dynamic_example_local_mock.yaml).
- Create config: see all options for `form_composer config` command [here](/mephisto/generators/form_composer/README.md#using-formcomposerconfig-utility). Example command:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      mephisto form_composer config --verify --directory "/mephisto/examples/form_composer_demo/data/dynamic_presigned_urls"
  ```
- Launch command after you generated all configs:
  ```shell
  docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task_dynamic_presigned_urls.py
  ```


# End-to-end example with AWS

Putting it altogether, let's prepare and launch a task featuring a form containing one embedded file plus a few other fields. Here we'll assume working in directory `/mephisto/examples/form_composer_demo/data/dynamic_presigned_urls`.

- Adjust `dynamic_presigned_urls_example_ec2_prolific.yaml` task config as needed
- Create `unit_config.json` file to define your form fields and layout
    - it should contain a token named `file_location`
    - for more details see `mephisto/generators/form_composer/README.md`
- Create `separate_token_values_config.json` with desired token values
- Specify your AWS credentials
    - Create file `docker/aws_credentials` and populate it with AWS keys info (for infrastructure and Mturk)
    - Populate your AWS credentials into `docker/envs/env.local` file (for presigning S3 URLs)
    - Clone file `docker/docker-compose.dev.yml` as `docker/docker-compose.local.yml`, and point its `env_file` to `envs/env.local`
    - Ensure `envs/env.local` file has a defeinition of these env variables:
        - `PROLIFIC_API_KEY`: set it to an empty string if you don't have a value yet
        - `CYPRESS_CACHE_FOLDER`: set it to any writable folder, e.g. `/tmp`
- Remove content of folder `/tmp` (if you didn't shut the previous Task run correctly)
- Launch docker containers: `docker-compose -f docker/docker-compose.local.yml up`
- SSH into the running container: `docker exec -it mephisto_dc bash`
- Generate your task data config with these commands:
  ```shell
  mephisto form_composer config \
    --directory "/mephisto/examples/form_composer_demo/data/dynamic_presigned_urls" \
    --update-file-location-values "https://your-bucket.s3.amazonaws.com/..." \
    --use-presigned-urls

  mephisto form_composer config \
    --directory "/mephisto/examples/form_composer_demo/data/dynamic_presigned_urls" \
    --permutate-separate-tokens

  mephisto form_composer config \
    --directory "/mephisto/examples/form_composer_demo/data/dynamic_presigned_urls" \
    --extrapolate-token-sets

  mephisto form_composer config \
    --directory "/mephisto/examples/form_composer_demo/data/dynamic_presigned_urls" \
    --verify
  ```
- Launch your task:
  ```shell
  cd /mephisto/examples/form_composer_demo && python run_task_dynamic_presigned_urls_ec2_prolific.py
  ```
- After the Task is completed by all workers, launch task review app and acces it at  [http://localhost:8081](http://localhost:8081) (for more details see `mephisto/review_app/README.md`):
  ```shell
  mephisto review_app --host 0.0.0.0 --port 8000 --debug --force-rebuild
  ```

_Note: if a package build was terminated/failed, or related source code was changed, FormComposer needs to be rebuilt with this command: `mephisto scripts form_composer rebuild_all_apps`._

---

# Your Mephisto project

To read on steps for creating your own custom Mephisto task, please refer to README in the main Mephisto repo.
