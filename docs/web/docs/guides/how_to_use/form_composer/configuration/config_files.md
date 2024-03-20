---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# Config files reference

This section is a reference on FormComposer's standard configuration files and object attributes.

## Config files structure

You will need to provide FormComposer with a JSON configuration of your form fields,
and place it in `generators/form-composer/data` directory.

- The task config file should be named `task_data.json`, and contain a list of JSON objects, each one with one key `form`.
- If you want to slightly vary your form within a Task (by inserting different values into its text), you need to add two files (that will be used to auto-generate `task_data.json` file):
    - `token_sets_values_config.json` containing a JSON array of objects (each with one key `tokens_values` and value representing name-value pairs for a set of text tokens to be used in one form version).
    - `form_config.json` containing a single JSON object with one key `form`.
    - For more details, read on about dynamic form configs.
- If you want to insert code (HTML or JS) into your form config, you need to create `insertions` directory in the form config directory, and place these files there
    - For more details, read on about insertions.

Working config examples are provided in `examples/form_composer_demo/data` directory:
- task data config: `simple/task_data.json`
- form config: `dynamic/form_config.json`
- token sets values config: `dynamic/token_sets_values_config.json`
- separate tokens values: `dynamic/separate_token_values_config.json` to create `token_sets_values_config.json`
- resulting extrapolated config: `dynamic/task_data.json`

_To understand what the concept of "tokens" means, see [Using multiple form versions](/docs/guides/how_to_use/form_composer/configuration/multiple_form_versions/) section._

---

## Config file: `task_data.json`

Task data config file `task_data.json` specifies layout of all form versions that are completed by workers. Here's an abbreviated example of such config:

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
              "instruction": "insertions/personal_info_instruction.html",
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
          ],
          "triggers": {
            "onClick": ["onClickSectionHeader", "FIRST"]
          }
        },
        { ... }
      ],
      "submit_button": {
        "text": "Submit",
        "tooltip": "Submit form"
      }
    }
  },
  ...
]
```

### Form config levels

Form UI layout consists of the following layers of UI object hierarchy:

1. Form
2. Section
3. Fieldset
4. Fields Row
5. Field


#### Form objects attributes

Each of the form hierarchy levels appears as an object in form's JSON config, with certain attributes.

While attributes values are limited to numbers and text, these fields (at any hierarchy level) also accept raw HTML values:
- `help`
- `instruction`
- `title`

_Note that, due to limitations of JSON format, HTML content needs to be converted into a single long string of text._

You can style fields with HTML-classes in `classes` attribute. You can use any bootstrap classes or our built-in classes:
- `hidden` - if you need to hide element and show it later with custom triggerm, but you do not need it be a fully hidden field (`"type": "hidden"`)
- `centered` - centered horizontally

TBD: Other classes and styles insertions


---

#### Config level: form

`form` is a top-level config object with the following attributes:

- `id` - Unique HTML id of the form, in case we need to refer to it from custom handlers code (String, Optional)
- `classes` = Custom classes that you can use to restyle element or refer to it from custom handlers code (String, Optional)
- `instruction` - HTML content describing this form; it is located before all contained sections (String, Optional)
- `title` - HTML header of the form (String)
- `submit_button` - Button to submit the whole form and thus finish a task (Object)
    - `id` - Unique HTML id of the button, in case we need to refer to it from custom handlers code (String, Optional)
    - `instruction` - Text shown above the "Submit" button (String, Optional)
    - `text` - Label shown on the button (String)
    - `tooltip` - Browser tooltip shown on mouseover (String, Optional)
    - `triggers` - Functions that are being called on available React-events (`onClick`, see [JS trigger insertion](/docs/guides/how_to_use/form_composer/configuration/insertions/#js-trigger-insertion))
- `sections` - **List of containers** into which form content is divided, for convenience; each section has its own validation messages, and is collapsible (Array[Object])

---

#### Config level: section

Each item of `sections` list is an object with the following attributes:

- `id` - Unique HTML id of the section, in case we need to refer to it from custom handlers code (String, Optional)
- `classes` = Custom classes that you can use to restyle element or refer to it from custom handlers code (String, Optional)
- `collapsable` - Whether the section will toggle when its title is clicked (Boolean, Optional, Default: true)
- `initially_collapsed` - Whether the section display will initially be collapsed (Boolean, Optional, Default: false)
- `instruction` - HTML content describing this section; it is located before all contained fieldsets (String, Optional)
- `name` - Unique string that serves as object reference when using dynamic form config (String)
- `title` - Header of the section (String)
- `fieldsets` - **List of containers** into which form fields are grouped by meaning (Array[Object])
- `triggers` - Functions that are being called on available React-events (`onClick` on header, see [JS trigger insertion](/docs/guides/how_to_use/form_composer/configuration/insertions/#js-trigger-insertion))

---

#### Config level: fieldset

Each item of `fieldsets` list is an object with the following attributes:

- `id` - Unique HTML id of the fieldset, in case we need to refer to it from custom handlers code (String, Optional)
- `classes` = Custom classes that you can use to restyle element or refer to it from custom handlers code (String, Optional)
- `instruction` - HTML content describing this fieldset; it is located before all contained field rows (String, Optional)
- `title` - Header of the section (String)
- `rows` - **List of horizontal lines** into which section's form fields are organized (Array[Object])

---

#### Config level: row

Each item of `rows` list is an object with the following attributes:

- `id` - Unique HTML id of the row, in case we need to refer to it from custom handlers code (String, Optional)
- `classes` = Custom classes that you can use to restyle element or refer to it from custom handlers code (String, Optional)
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
    "regexp": ["^[a-z\.\-']+$", "ig"]
    // or can use this --> "regexp": "^[a-z\.\-']+$"
  },
  "value": ""
}
```

---

### Attributes for "field" config level

#### `value` attribute

The `value` attribute specifies initial value of a field, and has the following format:

- String for `input`, `textarea`, `email`, `hidden`, `number`, `password`, `radio`, and `select` with `"multiple": false` field types
    - For `radio` and `select` fields, it must be one of the input options' values
- Object for `checkbox`
    - The object should consist of all checkbox options with their Boolean value, e.g. `{"react": true, "python": true, "sql": false}`
- Array<String\> for `select` with `"multiple": true`
    - All array items must be input options' values, e.g. `["python", "sql"]`


#### Attributes - all fields

The most important attributes are: `label`, `name`, `type`, `validators`

- `help` - HTML explanation of the field/fieldset displayed in small font below the field (String, Optional)
- `id` - Unique HTML id of the field, in case we need to refer to it from custom handlers code (String, Optional)
- `classes` = Custom classes that you can use to restyle element or refer to it from custom handlers code (String, Optional)
- `label` - Field name displayed above the field (String)
- `name` - Unique name under which this field's data will be sent to the server (String)
- `placeholder` - Text faintly displayed in the field before user provides a value (String, Optional)
- `tooltip` - Text shown in browser tooltip on mouseover (String, Optional)
- `type` - Type of the field (`input`, `email`, `select`, `textarea`, `checkbox`, `radio`, `file`, `hidden`) (String)
- `validators` - Validators preventing incorrect data from being submitted (Object[<String\>: String|Boolean|Number], Optional). Supported key-value pairs for the `validators` object:
    - `required`: Ensure field is not left empty (Boolean)
    - `minLength`: Ensure minimal number of typed characters or selected choices (Number)
    - `maxLength`: Ensure maximum number of typed characters or selected choices (Number)
    - `regexp`: Ensure provided value confirms to a Javascript regular expression. It can be:
        - (String): a regexp string (e.g. `"^[a-zA-Z0-9._-]+$"`) in which case default matching flags are `igm` are used
        - (2-item Array[String, String]): a regexp string followed by matching flags (e.g. `["^[a-zA-Z0-9._-]+$", "ig"]`)
    - `fileExtension`: Ensure uploaded file has specified extension(s) (e.g. `["doc", "pdf"]`) (Array<String\>)
- `value` - Initial value of the field (String, Optional)
- `triggers` - Functions that are being called on available React-events (`onClick`, `onChange`, `onBlur`, `onFocus`, see [JS trigger insertion](/docs/guides/how_to_use/form_composer/configuration/insertions/#js-trigger-insertion))


#### Attributes - file field

- `show_preview` - Show preview of selected file before the form is submitted (Boolean, Optional)


#### Attributes - select field

- `multiple` - Support selection of multiple provided options, not just one (Boolean. Default: false)
- `options` - list of available options to select from. Each option is an object with these attributes:
    - `label`: displayed text (String)
    - `value`: value sent to the server (String|Number|Boolean)


#### Attributes - checkbox and radio fields

- `options` - list of available options to select from. Each option is an object with these attributes:
    - `label`: displayed text (String)
    - `value`: value sent to the server (String|Number|Boolean)
    - `checked`: initial state of selection (Boolean, default: false)


## Config file: `form_config.json`

Form config file `form_config.json` specifies layout of a form in the same way as `task_data.json`, but with a few notable differences:
- It contains a single JSON object (not a JSON array of objects)
- Some of its form attributes definitions must contain dynamic tokens (whose values will be extrapolated, i.e. substituted with variable chunks of text) - see further below.


## Config file: `token_sets_values_config.json`

Sets of token values are specified as a JSON array of objects, where each object has one key `"tokens_values"`. Under that key there's a key-value definition of all tokens in that set.

Example:

```json
[
  {
    "tokens_values": {
      "model": "Volkswagen",
      "make": "Beetle",
      "review_criteria": "insertions/review_criteria.html"
    }
  },
  {
    "tokens_values": {
      "model": "Nissan",
      "make": "Murano",
      "review_criteria": "insertions/review_criteria.html"
    }
  }
]
```

## Config file: `separate_token_values_config.json`

Lists of separate tokens values are specified as JSON object with key-value pairs, where keys are token names, and values are JSON arrays of their values.

Example:

```json
{
  "actor": ["Carrie Fisher", "Keanu Reeves"],
  "genre": ["Sci-Fi"],
  "movie_name": ["Star Wars", "The Matrix"]
}

```
