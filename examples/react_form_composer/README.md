# Form Composer

This is a Task generator that provides Tasks for simple questionnaire projects.

---

### How to run

1. In repo root, launch containers: `docker-compose -f docker/docker-compose.dev.yml up`
2. SSH into running container to run server: `docker exec -it mephisto_dc bash`
3. Inside the container run server: 
   1. Build `form-composer` package `cd /mephisto/packages/form-composer && npm run build`
   2. Run project: `cd /mephisto/examples/react_form_composer && python ./run_task.py`

---

### How to configure

All you need to do is provide Form Builder with a JSON configuration of your form fields.

An example is found in `examples/react_form_composer/data/data.json` file.

---

### How form is composed

Form Builder supports several layers of hierarchy:

1. Section
2. Fieldset
3. Fields Row
4. Field

---

### Validators

Available validators:
 - `required` (boolean)
 - `minLength` (integer)
 - `maxLength` (integer)
 - `regexp` (string | array[string, string])

`regexp` params:
1. RedExp string (`"^[a-zA-Z0-9._-]+@mephisto\\.ai$"`). Default flags are `igm`
2. Array with RedExp string and flags (`["^[a-zA-Z0-9._-]+@mephisto\\.ai$", "ig"]`)

Example:

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
