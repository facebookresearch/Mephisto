These form-based questionnaires are example of FormComposer task generator.

---

## How to run

1. In repo root, launch containers: `docker-compose -f docker/docker-compose.dev.yml up`
2. SSH into running container to run server: `docker exec -it mephisto_dc bash`
3. Inside the container, run the project with either of these commands:
    - Simple form: `cd /mephisto/examples/form_composer_demo && python ./run_task.py`
    - Dynamic form: `cd /mephisto/examples/form_composer_demo && python ./run_task_dynamic.py`
    - Dynamic form with Prolific on EC2: `cd /mephisto/examples/form_composer_demo && python ./run_task_dynamic_ec2_prolific.py`
    - Dynamic form with Mturk on EC2: `cd /mephisto/examples/form_composer_demo && python ./run_task_dynamic_ec2_mturk_sandbox.py`

---

## How to configure

1. For simple form config you need to provide FormComposer with one JSON file - a configuration of your form fields. An example is found in `examples/form_composer_demo/data/simple/task_data.json` file.
2. For dynamic form configs you need two JSON files in `examples/form_composer_demo/data/dynamic` directory:
   - Form configuration `form_config.json`
   - Token sets values `token_sets_values_config.json`
   - To generate extrapolated `task_data.json` config, run this command: `mephisto form_composer_config --extrapolate-token-sets True`
       - Note that `task_data.json` file will be overwritten with the resulting config
3. To generate `token_sets_values_config.json` file from token values permutations in `separate_token_values_config.json`, run this command: `mephisto form_composer_config --permutate-separate-tokens`
    - Note that `token_sets_values_config.json` file will be overwriten with new sets of tokens values

---

#### Form config

For details on how form config is composed, and how its data fields are validated, please see the main FormComposer's [README.md](/mephisto/generators/form_composer/README.md).
