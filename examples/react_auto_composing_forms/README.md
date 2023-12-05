# Form Composer

This is a Task generator that provides Tasks for simple questionnaire projects.

---

### How to run

1. In repo root, launch containers: `docker-compose -f docker/docker-compose.dev.yml up`
2. SSH into running container to run server: `docker exec -it mephisto_dc bash`
3. Inside the container run server: `cd /mephisto/examples/react_auto_composing_forms && python ./run_task.py`

---

### How to configure

All you need to do is provide Form Builder with a JSON configuration of your form fields.

An example is found in `examples/react_auto_composing_forms/data/data.json` file.

---

### How form is composed

Form Builder supports several layers of hierarchy:

1. Section
2. Fieldset
3. Fields Row
4. Field
