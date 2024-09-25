---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 1
---

# Config files reference

This section is a reference on VideoAnnotators's standard configuration files and object attributes.

## Config files structure

You will need to provide VideoAnnotators with a JSON configuration of your form fields,
and place it in `generators/video_annotator/data` directory.

- The task config file should be named `task_data.json`, and contain a list of JSON objects, each one with one key `annotator`.
- If you want to slightly vary your form within a Task (by inserting different values into its text), you need to add two files (that will be used to auto-generate `task_data.json` file):
    - `token_sets_values_config.json` containing a JSON array of objects (each with one key `tokens_values` and value representing name-value pairs for a set of text tokens to be used in one form version).
    - `unit_config.json` containing a single JSON object with one key `annotator`.
    - For more details, read on about dynamic form configs.
- If you want to insert code (HTML or JS) into your form config, you need to create `insertions` directory in the form config directory, and place these files there
    - For more details, read on about insertions.

Working config examples are provided in `examples/video_annotator_demo/data` directory:
- task data config: `simple/task_data.json`
- annotator config: `dynamic/unit_config.json`
- token sets values config: `dynamic/token_sets_values_config.json`
- separate tokens values: `dynamic/separate_token_values_config.json` to create `token_sets_values_config.json`
- resulting extrapolated config: `dynamic/task_data.json`

_To understand what the concept of "tokens" means, see [Using multiple form versions](/docs/guides/how_to_use/video_annotator/configuration/multiple_form_versions/) section._

---

## Config file: `task_data.json`

Task data config file `task_data.json` specifies layout of all form versions that are completed by workers. Here's an abbreviated example of such config:

```json
[
  {
    "annotator": {
      "title": "Video Annotator example",
      "instruction": "<div class=\"instruction\">\n  Please annotate everything you think is necessary.\n</div>\n\n<style>\n  .instruction {\n    font-style: italic;\n  }\n</style>\n",
      "video": "https://my-bucket.s3.amazonaws.com/my-folder/video.mp4",
      "show_instructions_as_modal": true,
      "segment_fields": [
        {
          "id": "id_title",
          "label": "Segment name",
          "name": "title",
          "type": "input",
          "validators": {
            "required": true,
            "minLength": 1,
            "maxLength": 40
          }
        },
        {
          "id": "id_description",
          "label": "Describe what you see in this segment",
          "name": "description",
          "type": "textarea",
          "validators": {
            "minLength": 2,
            "maxLength": 500,
            "checkForbiddenWords": true
          },
          "triggers": {
            "onFocus": ["onFocusDescription", "\"Describe what you see in this segment\""]
          }
        },
        { ... }
      ],
      "submit_button": {
        "instruction": "If you are ready and think that you described everything, submit the results.",
        "text": "Submit",
        "tooltip": "Submit annotations"
      }
    },
    "annotator_metadata": {
      "tokens_values": {
        "video_path": "https://my-bucket.s3.amazonaws.com/my-folder/",
        "video_file": "video.mp4"
      }
    }
  },
  ...
]
```

### Unit config levels

VideoAnnotator UI layout consists of the following layers of UI object hierarchy:

1. Annotator
2. Submit Button


#### Annotator objects attributes

Each of the form hierarchy levels appears as an object in form's JSON config, with certain attributes.

While attributes values are limited to numbers and text, these fields (at any hierarchy level) also accept raw HTML values:
- `help`
- `instruction`
- `title`

_Note that, due to limitations of JSON format, HTML content needs to be converted into a single long string of text._

You can style fields with HTML-classes in `classes` attribute. You can use any bootstrap classes or our built-in classes:
- `centered` - centered horizontally

TBD: Other classes and styles insertions


---

#### Config level: annotator

`form` is a top-level config object with the following attributes:

- `id` - Unique HTML id of the form, in case we need to refer to it from custom handlers code (String, Optional)
- `classes` - Custom classes that you can use to restyle element or refer to it from custom handlers code (String, Optional)
- `instruction` - HTML content describing this form; it is located before all contained sections (String, Optional)
- `show_instructions_as_modal` - Enables showing `instruction` content as a modal (opened by clicking a sticky button in top-right corner); this make lengthy task instructions available from any place of a lengthy form without scrolling the page (Boolean, Optional, Default: false)
- `title` - HTML header of the form (String)
- `video` - URL to preuploaded video file (String)
- `segment_fields` - **List of fields** that will be added into each track segment
- `submit_button` - Button to submit the whole form and thus finish a task (Object)
    - `id` - Unique HTML id of the button, in case we need to refer to it from custom handlers code (String, Optional)
    - `instruction` - Text shown above the "Submit" button (String, Optional)
    - `text` - Label shown on the button (String)
    - `tooltip` - Browser tooltip shown on mouseover (String, Optional)
    - `triggers` - Functions that are being called on available React-events (`onClick`, see [JS trigger insertion](/docs/guides/how_to_use/video_annotator/configuration/insertions/#js-trigger-insertion))

---

#### Config level: field

Each item of `segment_fields` list is an object that corresponds to the track segment field displayed in the resulting Task UI page.

Here's example of a single field config:

```json
{
  "id": "id_title",
  "label": "Segment name",
  "name": "title",
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

- String for `input`, `textarea`, `email`, `number`, `password`, `radio`, and `select` with `"multiple": false` field types
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
- `value` - Initial value of the field (String, Optional)
- `triggers` - Functions that are being called on available React-events (`onClick`, `onChange`, `onBlur`, `onFocus`, see [JS trigger insertion](/docs/guides/how_to_use/video_annotator/configuration/insertions/#js-trigger-insertion))


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

_Note that, comparing FormComposer, VideoAnnotator segments do not have fields `file` and `hidden`._

## Config file: `unit_config.json`

Unit config file `unit_config.json` specifies layout of an annotator in the same way as `task_data.json`, but with a few notable differences:
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
