<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

This package provides `FormComposer` widget for React-based front-end development for Mephisto tasks.


# How to Run

To create and launch a Form Composer task, create a configuration that fits your needs,
and then the below commands.

---

#### Installation

```shell
cd /mephisto/packages/react-form-composer && npm install --save react-form-composer
```

#### Building

```shell
cd /mephisto/packages/react-form-composer && npm run build
```

#### Launching

```shell
# Sample launching commands
mephisto form_composer
mephisto form_composer --manual-versions True
mephisto form_composer --files-folder "https://s3.amazon.com/...."
```

where
- `-m/--manual-versions` argument skips auto-generating form versions in `data.json` by extrapolating token values, and instead uses an existing `data.json` file (see [Custom form versions](#custom-form-versions) section)
- `-f/--files-folder` argument generates token values based on file names found within specified file folder (see a separate section about this mode of running Form Composer)

Using Docker Compose:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --rm mephisto_dc \
    mephisto form_composer
```

Once it launches, in Docker console you will see links like this: http://localhost:3000/?worker_id=x&assignment_id=1 To view your Task as a worker, take one of these links, replace port 3000 with a port from your `docker-compose` config (e.g. for `3001:3000` it will be 3001), and paste it in your browser.


# Config file structure

- You will need to provide Form Composer with a JSON configuration of your form fields.
The form config file should be named `form_config.json`, and contain a JSON object with one key `form`.
- If you want to slightly vary your form within a Task (by inserting different values into its text), you need to add a file named `tokens_values_config.json` and containing a JSON array of objects, each with one key `tokens_values` and value representing name-value pairs for the text tokens.
    - For more details, read about dynamic form configs further down.

Config examples:
- form config: `examples/form_composer_demo/data/dynamic/form_config.json`
- token values config: `examples/form_composer_demo/data/dynamic/tokens_values_config.json`
- resulting extrapolated config: `examples/form_composer_demo/data/dynamic/data.json`

Here's a brief example of a form config:

```json
[
  {
    "form": {
      "title": "Form example",
      "instruction": "Please answer all questions to the best of your ability as part of our study.",
      "sections": [
        // Two sections
        {
          "name": "section_about",
          "title": "About you",
          "instruction": "Please introduce yourself. We would like to know more about your background, personal information, etc.",
          "fieldsets": [
            // Two fieldsets
            {
              "title": "Personal information",
              "instruction": "",
              "rows": [
                // Two rows
                {
                  "fields": [
                    {
                      "help": "",
                      "id": "id_name_first",
                      "label": "First name",
                      "name": "name_first",
                      "placeholder": "Type first name",
                      "tooltip": "Your first name",
                      "type": "input",
                      "validators": {
                        "required": true,
                        "minLength": 2,
                        "maxLength": 20
                      },
                      "value": ""
                    }
                  ],
                  "help": "Please use your legal name"
                },
                { ... }
              ]
            },
            {
              "title": "Cultural background",
              "instruction": "Please tell us about your cultural affiliations and values that you use in your daily life.",
              "rows": [
                // One row
                {
                  "fields": [
                    {
                      ...
                      "multiple": false,
                      "options": [
                        ...
                        {
                          "label": "United States of America",
                          "value": "USA"
                        },
                        ...
                      ],
                      "type": "select",
                      ...
                    }
                  ]
                }
              ],
              "help": "This information will help us compile study statistics"
            }
          ]
        },
        { ... }
      ],
      "submit_button": {
        "text": "Submit",
        "tooltip": "Submit form"
      }
    }
  }
]
```

---

## Form config levels

Form UI layout consists of the following layers of UI object hierarchy:

1. Form
2. Section
3. Fieldset
4. Fields Row
5. Field


###### Form objects attributes

Each of the form hierarchy levels appears as an object in form's JSON config, with certain attributes.

While attributes values are limited to numbers and text, these fields (at any hierarchy level) also accept raw HTML values:
- `help`
- `instruction`
- `title`

---

#### Config level: form

`form` is a top-level config object with the following attributes:

- `instruction` - HTML content describing this form; it is located before all contained sections (String, Optional)
- `title` - Header of the form (String)
- `submit_button` - Button to submit the whole form and thus finish a task (Object)
    - `text` - Label shown on the button
    - `tooltip` - Browser tooltip shown on mouseover
- `sections` - **List of containers** into which form content is divided, for convenience; each section has its own validation messages, and is collapsible (Array[Object])

---

#### Config level: section

Each item of `sections` list is an object with the following attributes:

- `collapsable` - Whether the section will toggle when its title is clicked (Boolean, Optional, Default: true)
- `initially_collapsed` - Whether the section display will initially be collapsed (Boolean, Optional, Default: false)
- `instruction` - HTML content describing this section; it is located before all contained fieldsets (String, Optional)
- `name` - Unique string that serves as object reference when using dynamic form config (String)
- `title` - Header of the section (String)
- `fieldsets` - **List of containers** into which form fields are grouped by meaning (Array[Object])

---

#### Config level: fieldset

Each item of `fieldsets` list is an object with the following attributes:

- `instruction` - HTML content describing this fieldset; it is located before all contained field rows (String, Optional)
- `title` - Header of the section (String)
- `rows` - **List of horizontal lines** into which section's form fields are organized (Array[Object])

---

#### Config level: row

Each item of `rows` list is an object with the following attributes:

- `fields` - **List of fields** that will be lined up into one horizontal line

---

#### Config level: field

Each item of `fields` list is an object that corresponds to the actual form field displayed in the resulting Task UI page.

Here's example of a single field config:

```json
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
    // or can use this --> "regexp": "^[a-zA-Z0-9._-]+@mephisto\\.ai$"
  },
  "value": ""
}
```

###### Attributes - all fields

The most important attributes are: `label`, `name`, `type`, `validators`

- `help` - HTML explanation of the field displayed in small font below the field (String, Optional)
- `id` - Unique HTML id of the field, in case we need to refer to it from custom handlers code (String, Optional)
- `label` - Field name displayed above the field (String)
- `name` - Unique name under which this field's data will be sent to the server (String)
- `placeholder` - Text faintly displayed in the field before user provides a value (String, Optional)
- `tooltip` - Text shown in browser tooltip on mouseover (String, Optional)
- `type` - Type of the field (`input`, `email`, `select`, `textarea`, `checkbox`, `radio`, `file`) (String)
- `validators` - Validators preventing incorrect data from being submitted (Object[<String>: String|Boolean|Number], Optional). Supported key-value pairs for the `validators` object:
    - `required`: Ensure field is not left empty (Boolean)
    - `minLength`: Ensure minimal number of typed characters or selected choices (Number)
    - `maxLength`: Ensure maximum number of typed characters or selected choices (Number)
    - `regexp`: Ensure provided value confirms to a Javascript regular expression. It can be:
        - (String): a regexp string (e.g. `"^[a-zA-Z0-9._-]+$"`) in which case default matching flags are `igm` are used
        - (2-item Array[String, String]): a regexp string followed by matching flags (e.g. `["^[a-zA-Z0-9._-]+$", "ig"]`)
- `value` - Initial value of the field (String, Optional)


###### Attributes - select field

- `multiple` - Support selection of multiple provided options, not just one (Boolean. Default: false)
- `options` - list of available options to select from. Each option is an object with these attributes:
    - `label`: displayed text (String)
    - `value`: value sent to the server (String|Number|Boolean)


###### Attributes - checkbox and radio fields

- `options` - list of available options to select from. Each option is an object with these attributes:
    - `label`: displayed text (String)
    - `value`: value sent to the server (String|Number|Boolean)
    - `checked`: initial state of selection (Boolean, default: false)


# Dynamic form config

If you wish to slightly vary form instructions within the same Task (e.g. show different images or different text), you should use a dynamic form config.

---

## Dynamic form config files

Dynamic form config consists of two parts:

- `form_config.json`: tokenized form config - same as non-dynamic form config, except it may contain tokens within certain objects attributes (see [Tokens extrapolation](#tokens-extrapolation))
- `tokens_values_config.json`: file containing sets of token values, where each set is plugged into a dynamic form config to generate its form version (each form version will be completed by `units_per_assignment` different workers).


#### Extrapolated config

During bulding a Task with dynamic form config, the resulting config containing all form vesions will be placed in `data.json` file (next to `form_config.json` file).

- In your YAML Task config, always refer to the extrapolated config file `data.json` (not the foorm config file)
- Every time you re-run Form Composer, `data.json` file will be overwritten
- Run generator with command: `mephisto form_composer`


#### Custom form versions

Suppose your form variations go beyond slight text changes (e.g. you wish to add a fieldset in one version of form config). In that case:

- Create your own `data.json` file manually (it will be basically a JSON list of copy-pasted individual form config versions)
- You don't need to create `form_config.json` and `tokens_values_config.json` files
- Run generator with command: `mephisto form_composer --manual-versions True`

---

## Tokens extrapolation

A token is a named text placeholder that gets replaced ("extrapolated") by values specified in `tokens_values_config.json` (each set of `tokens_values` specifies a form version, and contains one such value).

Token placeholders within an attribute looks like so: `{{TOKEN_NAME}}`

Tokens can be placed within the following object attributes:

- `help`
- `instruction`
- `label`
- `title`
- `tooltip`

When reusing a token with same name in different form attributes (across all levels of form config), you should specify it in each `tokens_values` just once, for convenience.
(This also means that token names must be unique within the entire form config.)


---

## Dynamic form config with `--files-folder`

Consider a special case when form config has only one token, a file path. Form Composer offers a shortcut to save your time on creating `tokens_values_config.json` file in this scenario. Simply launch task with this command:

```
mephisto form_composer --files-folder [value]
```

Argument `--files-folder [value]` does the following:
- finds folder specified by `[value]`, which currently can be an S3 folder URL like `"https://s3.amazon.com/...."`
- finds (recursively) location of all files within that folder (e.g. S3 URLs)
- generates `tokens_values_config.json` file that looks like so:
```json
[
  {
    "tokens_values": {
      "file_location": "[location/of/file1]",
    }
  },
  {
    "tokens_values": {
      "file_location": "[location/of/file2]"
    }
  },
  ...
]
```
- now that tokens values config is generated, Task launch proceeds like for a normal dynamic form config

Note that:
- `form_config.json` file must contain one, and only one, token name `{{file_location}}`
- `tokens_values_config.json` file is not needed in this case (it will be auto-generated)

---

## Embedding FormBuilder into custom application

If you wish to embed FormComposer in your custom application, a few tips about extrapolator function `mephisto.generators.form_composer.configs_validation.extrapolated_config.create_extrapolated_config` (that generates extrapolated `data.json` config):

- call extrapolator function if you want to extrapolate token values
    - You can see how it's done from [Example docs](#live-examples) here and by exploring source code of [run_task_dynamic.py](/examples/form_composer_demo/run_task_dynamic.py) module.
- NOT call extrapolator function if you already have a custom `data.json` config

---

## Config files example


#### Form config

Here's how fields with tokens look like in `form_config.json` file:

```json
{
  ...
  "instruction": "Rate {{actor}}'s performance in movie <b>'{{movie_name}}'</b>",
  ...
  "help": "Please only consider the movie '{{movie_name}}'",
  ...
}
...
{
  ...
  "instruction": "Rate the plot in movie '{{movie_name}}'?",
  ...
}
```


#### Token values config

Here's how token values are specified `tokens_values_config.json` file:

```json
[
  {
    "tokens_values": {
      "actor": "Carrie Fisher",
      "movie_name": "Star Wars"
    }
  },
  {
    "tokens_values": {
      "actor": "Keanu Reeves",
      "movie_name": "The Matrix"
    }
  }
]
```


#### Extrapolated config

This is how resulting `data.json` file will look like, after form attributes from `form_config.json` get extrapolated with values from `tokens_values_config.json`:

```json
// First extrapolated form version
{
  ...
  "instruction": "Rate Carrie Fisher's performance in movie <b>'Star Wars'</b>",
  ...
  "help": "Please only consider the movie 'Star Wars'",
  ...
}
...
{
  ...
  "instruction": "Rate the plot in movie 'Star Wars'?",
  ...
},
// Second extrapolated form version
{
  ...
  "instruction": "Rate Keanu Reeves's performance in movie <b>'The Matrix'</b>",
  ...
  "help": "Please only consider the movie 'The Matrix'",
  ...
}
...
{
  ...
  "instruction": "Rate the plot in movie 'The Matrix'?",
  ...
}
```

Once a Task is launched, each of these two form versions will be completed `units_per_assignment` times (by different workers)


---

## Custom field handlers

TBD

---

## Live Examples

You can investigate live examples of Form Composer in `examples/form_composer_demo` directory,

For more details on how to run these examples, refer to this [README.md](/examples/form_composer_demo/README.md).
