<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# About Mephisto

## Purpose

The purpose of Mephisto is to run a data collection project that you can launch it locally or on a remote machine. A launched project (TaskRun) does the following:

- Builds necessary infra with an Architect (local-based mock, or cloud-based EC2/Heroku)
- The infra server does the following, until specified number of Task Units is reached:
  - It generates a link where a worker can provide their project input (Task Unit)
  - The links are sent to a human cloud (Provider), and a worker clicks on the link
  - The links displays a UI task template (Task App) to the worker; submitting the task sends worker's input to the infra server
  - The infra server sends (via a web socket) data to the TaskRun that you're running locally
  - TaskRun stores the data in local database/files, and dispatches new Task Units as needed
- Finally, you can review worker input using Review App, and export the data out of the database as needed.

---

## Architecture

This is the main package directory, containing all of the core workings of Mephisto. They roughly follow the divisions noted in the [architecture overview doc](https://github.com/facebookresearch/Mephisto/blob/main/docs/architecture_overview.md#agent). The breakdown is as following:

- `abstractions`: Contains the interface classes for the core abstractions in Mephisto, as well as implementations of those interfaces. These are the Architects, Blueprints, Crowd Providers, and Databases.
- `client`: Contains user interfaces for using Mephisto at a very high level. Primarily comprised of the python code for the cli and the web views, such as Review App.
- `data_model`: Contains the data model components as described in the architecture document. These are the relevant data structures that build upon the underlying MephistoDB, and are utilized throughout the Mephisto codebase.
- `operations`: Contains low-level operational code that performs more complex functionality on top of the Mephisto data model.
- `scripts`: Contains commonly executed convenience scripts for Mephisto users.
- `tools`: Contains helper methods and modules that allow for lower-level access to the Mephisto data model than the clients provide. Useful for creating custom workflows and scripts that are built on Mephisto.

#### Providers

Provider is a host of human cloud, or worker crowd. Currently the following Providers are supported:

- `Mock` - runs locally, assuming your machine has a static IP. Used for testing and elementary projects.
- `MTurk` - Amazon Mechanical Turk provider (will eventually be deprecated)
- `MTurk Sandbox` - testing setup for Mturk
- `Prolific` - a human cloud prvider that's more reliable than Mturk, albeit with fewer workers

#### Architects

Architect is the manager of infrastructure of a project. Currently we support the following infrastructure hosts:

- `local` - your local machine, assuming it has a static IP address.
- `ec2` - AWS EC2 servers (in FAIR cluster)
- `heroku` - Heroku servers (no future development, in maintenance mode)
- `mock` - used for testing, for example, in Mephisto's unittests

---

# Sample Mephisto projects

Mephisto repo contains several sample projects (they're called Tasks). If you don't want to engage any cloud infrastructure, you can run all sample projects on a local machine with `mock` architect.

Sample Tasks may contain several YAML configuration files. Their naming pattern follows convention `<base_name>_<architect>_<provider>.yaml`.

A few notes:
- For any architect project data will be stored in SQLite databases and local files.
- If a project breaks and does not shut down cleanly, you may need to remove `tmp` directory in repo root before re-launching. (Otherwise you could see errors like Prometeus cannot start, etc.)
- To see more browser links for task units (assignments) within a TaskRun, check console logs (and remember to use correct port)
- If you terminate a TaskRun, you can launch it again, and results from all TaskRuns will be automatically collated
- Note that most detailed logs are written into files in `outputs/` directory in repo root (not in the console)

---

# Collected Task data

A quick overview on how to work with data collected through Mephisto Tasks.

## Review collected data

After running the above examples, your local database will contain some input from workers. You can review it, and assign qualifications to those workers, using Mephisto's Review App.

- Launch command:
```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --rm mephisto_dc \
    mephisto review_app -h 0.0.0.0 -p 8000 -d True -f False -s False
```
- Browser page: [http://localhost:8081/](http://localhost:8081/).

The UI is fairly intuitive, and for more details you can consult [README.md for TaskReview app](/mephisto/review_app/README.md).

---

## Export collected data

The easiest way to export raw data for the entire Task is to click Export button for that Task in Mephisto's Review App.
The below explains in more detail how data storage is organized (e.g. for manual export).

All TaskRun data is stored in `data` directory of repo root:

- `data/database.db` is Mephisto's main SQLite database with generic objects data
  - Note that its DB schema is defined in `mephisto/abstractions/databases/local_database.py` file
- `data/data` folder contains helper files, such as detailed input/output data in JSON
- `data/mock/mock.db` or `data/mturk/mturk.db` or `data/prolific/prolific.db` is Provider-specific SQLite database (DB schema varies greatly depending on the provider).

Worker responses metadata are in these databases, and actual data of their responses in these folders. After TaskRun is completed and results are reviewed, you can access workers raw responses using `mephisto/tools/examine_utils.py` script

---

# Create your own Task

Here's a list of steps on how to build and run your own custom data collection Task to run on Mephisto.

## Write Task App code

In order to launch your own customized project, you will need to write a React app that will display instructions/inputs to workers. You can start by duplicating an existing Task App code (e.g. `examples/static_react_task` directory) and customizing it to your needs. The process goes like this:

1. Copy `static_react_task` directory to your project directory within Mephisto repo
2. Customize task's back-end code in `run_task.py` script to pass relevant data to `SharedStaticTaskState`, set `shared_state.prolific_specific_qualifications`, `shared_state.qualifications` (for custom qualifications), etc
3. Customize task-related parameters variables in your `conf/<my_new_config>.yaml` file as needed.
  - Some examples of variables from `blueprint` category are:
    - `extra_source_dir`: optional path to sources that Task App may refer to (images, video, css, scripts, etc)
    - `data_json`: path to a json file containing task data
  - To see other configurable blueprint variables, type `mephisto wut blueprint=static_task`
4. Customize task's front-end code, with starting point being `/<my_task_folder>/webapp/src/components/core_components.jsx` (you caninclude an onboarding step if you like).
5. Add the ability to review results of your task app. In short, you need to implement additional component or logic to render json data that TaskReview app will provide. For more details, read this [doc](/mephisto/review_app/README.md).
6. Run `run_task.py` to dry-run your task on localhost.
7. Repeat 5 & 6 until you're happy with your task.
8. Launch a small batch with a chosen crowd provider to see how real workers handle your task.
9. Iterate more.
10. Collect some good data.

---

## Configure Task parameters

This is a sample YAML configuration to run your Task on **AWS EC2** architect with **Prolific** provider

1. Set Prolific as your provider
    ```yaml
    defaults:
      - /mephisto/provider: prolific
    ```

2. Set EC2 as an architect
    ```yaml
    defaults:
      - /mephisto/architect: ec2
    mephisto:
      architect:
        _architect_type: ec2
        profile_name: mephisto-router-iam
        subdomain: "2023-08-23.1"
    ```

    Where:
      - `profile_name` - EC2 service profile name (used for authentication and domain name selection)
      - `subdomain` - must be unique across all TaskRuns. Subdomain on which workers can access their Task Unit

3. Set Prolific-specific task parameters. Sample parameters could look similar to this:
    ```yaml
    mephisto:
        provider:
          prolific_id_option: "url_parameters"
          prolific_workspace_name: "My Workspace"
          prolific_project_name: "My Project"
          prolific_allow_list_group_name: "Allow list"
          prolific_block_list_group_name: "Block list"
          prolific_eligibility_requirements:
            - name: "CustomWhitelistEligibilityRequirement"
              white_list:
                - 6463d32f50a18041930b71be
                - 6463d3922d7d99360896228f
                - 6463d40e8d5d2f0cce2b3b23
            - name: "ApprovalRateEligibilityRequirement"
              minimum_approval_rate: 1
              maximum_approval_rate: 100
    ```

    For all available Prolific-specific parameters see `mephisto.abstractions.providers.prolific.prolific_provider.ProlificProviderArgs` class
    and [Prolific API Docs](https://docs.prolific.com/docs/api-docs/public/#tag/Studies).

    Note that `prolific_eligibility_requirements` does not include custom worker qualifications, these are maintained in your local Mephisto database. These can be specified in a Task launching script (usually called `run_task.py`, for example, `examples/simple_static_task/run_task.py`)

---

## Launch TaskRun

1. Specify auth credentials for your Prolific account. To do so, you need to run command
    ```shell
    mephisto register prolific name=prolific api_key=API_KEY_FOR_YOUR_PROLIFIC_ACCOUNT
    ```
or simply embed that command into your docker-compose entrypoint script.

2. Launch a new TaskRun (instead of `examples/simple_static_task` below specify path to your own Task code; `HYDRA_FULL_ERROR=1` is optional and prints out detailed error info)

    ```shell
    docker-compose -f docker/docker-compose.dev.yml run \
        --build \
        --rm mephisto_dc \
        rm -rf /mephisto/tmp && \
        HYDRA_FULL_ERROR=1 python /mephisto/examples/simple_static_task/run_task.py
    ```

  This TaskRun script will spin up an EC2 server, upload your React Task App to it, and create a Study on Prolific. Now all eligible workers will see your Task Units (with links poiting to EC2 server) on Prolific, and can complete it.

3. Leave the Task running in the console until all worker submissions are received. If TaskRun was interrupted, you can restart it using the same commands. After all submissions are received, the Architect will automatically shut down actiive TaskRun.

4. Now you are ready to review, and then download, your Task results.

---

## Process results

Final steps of reviewing worker submissions and exporting the results will be same as described under sample Mephisto project runs.

---

## Launch Auto-composed forms

1. Create `data.json` config in `mephisto/generators/form_composer/data`. An example is found in `examples/simple_form_composer/data/data.json` file
2. Run a task with command:
    - Locally `mephisto form_composer`
    - Using Docker Compose
      ```shell
      docker-compose -f docker/docker-compose.dev.yml run \
          --build \
          --publish 8081:8000 \
          --rm mephisto_dc \
          mephisto form_composer
      ```
3. Open in Browser page: http://localhost:3001/
