These video annotators are example of VideoAnnotator task generator.

---

## How to run

1. In repo root, launch containers: `docker-compose -f docker/docker-compose.dev.yml up`
2. SSH into running container to run server: `docker exec -it mephisto_dc bash`
3. Inside the container, run the project with either of these commands:
    - Simple form: `cd /mephisto/examples/video_annotator_demo && python ./run_task.py`

---

## How to configure

1. For simple unit config you need to provide VideoAnnotator with one JSON file - a configuration of annotator. An example is found in `examples/video_annotator_demo/data/simple/task_data.json` file.

<!--- # TODO
2. For dynamic annotator configs you need two JSON files in `examples/video_annotator_demo/data/dynamic` directory:
   - Unit configuration `unit_config.json`
   - Token sets values `token_sets_values_config.json`
   - To generate extrapolated `task_data.json` config, run this command: `mephisto video_annotator config --extrapolate-token-sets True`
       - Note that `task_data.json` file will be overwritten with the resulting config
3. To generate `token_sets_values_config.json` file from token values permutations in `separate_token_values_config.json`, run this command: `mephisto video_annotator config --permutate-separate-tokens`
    - Note that `token_sets_values_config.json` file will be overwriten with new sets of tokens values
-->

---

#### Unit config

For details on how unit config is composed, and how its data fields are validated, please see the main VideoAnnotator's [README.md](/mephisto/generators/video_annotator/README.md).
