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

```bash
cd /mephisto/packages/form-composer && npm install --save form-composer
```

#### Building
```bash
cd /mephisto/packages/form-composer && npm run build
```

---

## How to configure

You will need to provide Form Builder with a JSON configuration of your form fields.
The config file name should be `data.json`, and it should contain a single-item JSON array with one key `form`.

An example is found in `examples/react_form_composer/data/data.json` file.

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

TBD

---

## Custom field handlers

TBD
