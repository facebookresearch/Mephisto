This form-based questionnaire is a simple example of Form Composer task generator.

---

### How to run

1. In repo root, launch containers: `docker-compose -f docker/docker-compose.dev.yml up`
2. SSH into running container to run server: `docker exec -it mephisto_dc bash`
3. Inside the container run server:
   1. Build `react-form-composer` package `cd /mephisto/packages/react-form-composer && npm run build`
   2. Run project with
       - simple data config: `cd /mephisto/examples/form_composer_demo && python ./run_task.py`
       - dynamic data configs: `cd /mephisto/examples/form_composer_demo && python ./run_task_dynamic.py`

---

### How to configure

1. For simple data config you need to provide Form Composer with one JSON file - a configuration of your form fields.
An example is found in `examples/form_composer_demo/data/simple/data.json` file.
2. For dynamic data configs you need two JSON files:
   - form configuration `examples/form_composer_demo/data/dynamic/form_config.json`
   - tokens values `examples/form_composer_demo/data/dynamic/tokens_values_config.json`

Note that during bulding a Task with dynamic form config, the resulting data config will be placed in `data.json` file, i.e. `examples/form_composer_demo/data/dynamic/data.json` (in this example it's already been created and will be overwritten when you build a Task).

---

### Form config

For details on how form config is composed, and how data fields are validated please see the main Form Composer's README.

Here's a sample part of form config:

```json
{
    "fields": [
        {
          "id": "id_name_first",
          "label": "First name",
          "name": "name_first",
          "placeholder": "Type first name",
          "title": "First name of a person",
          "type": "input",
          "validators": {
            "required": true,
            "minLength": 2,
            "maxLength": 20,
            "regexp": ["^[a-zA-Z0-9._-]+@mephisto\\.ai$", "ig"]
            // or just string "regexp": "^[a-zA-Z0-9._-]+@mephisto\\.ai$"
          },
          "value": ""
        }
    ]
}
```
