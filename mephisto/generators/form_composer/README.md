<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# Form Composer

This package provides `FormComposer` widget for React-based front-end development for Mephisto tasks.

---

## How to Run

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
mephisto form_composer
```

Using Docker Compose
```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --rm mephisto_dc \
    mephisto form_composer
```

Open in Browser page: http://localhost:3001/

---

## How to configure

You will need to provide Form Composer with a JSON configuration of your form fields.
The form config file name should be `form_config.json`, and it should contain a JSON object with one key `form`.
If you want to use more than one unit configuration and pass different values in form, you need to add `tokens_values_config.json` as well.
This config is a JSON array object with JSON object items with one key `tokens_values` that is object where is a key is a token and its value is value that will be the substitution for this token in form.

Config examples:
  - form config is found in `examples/simple_form_composer/data/dynamic/form_config.json` file
  - tokens values config is found in `examples/simple_form_composer/data/dynamic/tokens_values_config.json` file
  - resulting config is found in `examples/simple_form_composer/data/dynamic/data.json` file

Shortened example to ha more clear view before we dig deeper:
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

#### Form config hierarchy levels

Form UI layout consists of the following layers of UI object hierarchy:

1. Form
2. Section
3. Fieldset
4. Fields Row
5. Field

---

#### Config level: form

`form` is a top-level config object with the following attributes:

- `instruction` - Text describing this form; it is located before all contained sections (String, Optional)
- `title` - Header of the form (String)
- `submit_button` - Button to submit the whole form and thus finish a task (Object)
  - `text` - Label shown on the button
  - `tooltip` - Browser tooltip shown on mouseover
- `sections` - List of containers into which form content is divided, for convenience; each section has its own validation messages, and is collapsible (Array[Object])

---

#### Config level: section

Each item of `sections` list is an object with the following attributes:

- `instruction` - Text describing this section; it is located before all contained fieldsets (String, Optional)
- `title` - Header of the section (String)
- `name` - Unique string that serves as object reference when using dynamic form config (String)
- `fieldsets` - List of containers into which form fields are grouped by meaning (Array[Object])

---

#### Config level: fieldset

Each item of `fieldsets` list is an object with the following attributes:

- `instruction` - Text describing this fieldset; it is located before all contained field rows (String, Optional)
- `title` - Header of the section (String)
- `rows` - List of horizontal lines into which section's form fields are organized (Array[Object])

---

#### Config level: row

Each item of `rows` list is an object with the following attributes:

- `fields` - List of one or more fields that will be line up into one horizontal line

---

#### Config level: field

Each item of `fields` list is an object that corresponds to the actual form field displayed in the resulting Task UI page.

Example of a field config:

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

- `help` - Explanation of the field displayed in small font below the field (String, Optional)
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

---

## Dynamic form config

If you wish to slightly vary form instructions within the same Task (e.g. show different images or different text), you should use a dynamic form config.

---

#### Dynamic form config files

Dynamic form config consists of two parts:

- `form_config.json`: tokenized form config - same as non-dynamic form config, except it may contain tokens within certain fields
- `tokens_values_config.json`: file containing sets of token values, where each set is plugged into a dynamic form config to generate its form version (each form version will be completed by `units_per_assignment` different workers).


###### Extrapolated config

During bulding a Task with dynamic form config, the resulting config containing all form vesions will be placed in `data.json` file (next to `form_config.json` file).

- In your YAML Task config, always refer to the extrapolated config file `data.json` (not the foorm config file)
- Every time you re-run Form Composer, `data.json` file will be overwritten
- If you're writing your own application that includes Form Composer, use `mephisto.generators.form_composer.configs_validation.extrapolated_config.create_extrapolated_config` function to generate the extrapolated `data.json` config


###### Custom form versions

Suppose your form variations go beyond slight text changes (e.g. you wish to add a fieldset in one version of form config). In that case:

- Create your own `data.json` file manually (it will be a JSON list of copy-pasted individual form config versions)
- You don't need to create `form_config.json` and `tokens_values_config.json` files
- Do not call `mephisto.generators.form_composer.configs_validation.extrapolated_config.create_extrapolated_config` function in your code (you already have a `data.json` file ready)


---

#### Tokens extrapolation

A token is a named text placeholder that gets replaced ("extrapolated") by values specified in `tokens_values_config.json` (each set of `tokens_values` specifies a form version, and contains one such value).

Token placeholders within a field looks like so: `{{TOKEN_NAME}}`

Tokens can be placed within the following fields of a dynamic form config:

- `help`
- `instruction`
- `label`
- `title`
- `tooltip`


When reusing a token with same name in different form fields (at any level of form config), you should specify it in each `tokens_values` just once, for convenience. (This also means that token names must be unique across the entire form config.)

---

#### Config files example


###### Form config

Here's how fields with tokens look like in `form_config.json` file:

```json
{
  ...
  "instruction": "Rate {{actor}}'s performance in movie '{{movie_name}}'",
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


###### Token values config

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


###### Extrapolated config

This is how resulting `data.json` file will look like, after form fields from `form_config.json` get extrapolated with values from `tokens_values_config.json`:

```json
// First extrapolated form version
{
  ...
  "instruction": "Rate Carrie Fisher's performance in movie 'Star Wars'",
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
  "instruction": "Rate Keanu Reeves's performance in movie 'The Matrix'",
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

You can investigate live examples of Form Composer in `examples/simple_form_composer` directory,

For more details on how to run these examples, refer to this [README.md](examples/simple_form_composer/README.md).
