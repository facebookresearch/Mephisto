<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

This package provides `FormComposer` widget for React-based front-end development for Mephisto tasks.

You can find working demo of FormComposer in `examples/form_composer_demo`

- For details on how to run these examples, refer to the demo's [README.md](/examples/form_composer_demo/README.md)


# How to Run

To create and launch a FormComposer task, create your JSON form configuration,
and then run the below commands.

Once FormComposer launches, in the console you will see links like this:
http://localhost:3000/?worker_id=x&assignment_id=1

To view your Task as a worker, take one of these links and paste it in your browser.
If launched with `docker-compose`, replace 3000 with the remapped port (e.g. for `3001:3000` it will be 3001).


#### With docker-compose

You can launch FormComposer inside a Docker container:

1. Prepare configs (`form_composer_config` command)

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --rm mephisto_dc \
    mephisto form_composer_config --extrapolate-token-sets
```

2. Run composer itself (`form_composer` command)

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --publish 3001:3000 \
    --rm mephisto_dc \
    mephisto form_composer
```

#### Without docker-compose

First ensure that mephisto package is installed locally - please refer to [Mephisto's main doc](https://mephisto.ai/docs/guides/quickstart/).
Once that is done, run `form_composer_config` command(s) if needed, and then `form_composer` command:

```shell
mephisto form_composer_config --extrapolate-token-sets
mephisto form_composer
mephisto form_composer --task-data-config-only
```


## Using `form_composer_config` utility

The `form_composer_config` utility command helps auto-generate FormComposer config. It supports several options:

```shell
# Sample launching commands
mephisto form_composer_config --update-file-location-values "https://s3.amazonaws.com/..." --use_presigned_urls
mephisto form_composer_config --update-file-location-values "https://s3.amazonaws.com/..."
mephisto form_composer_config --permutate-separate-tokens
mephisto form_composer_config --extrapolate-token-sets
mephisto form_composer_config --verify
# Parameters that work together
mephisto form_composer_config --directory /my/own/path/to/data/ --verify
mephisto form_composer_config --directory /my/own/path/to/data/ --extrapolate-token-sets
mephisto form_composer_config --update-file-location-values "https://s3.amazonaws.com/..."
```

where
- `-d/--directory` - a **modifier** for all `form_composer_config` command options that specifies the directory where all form JSON config files are located (if missing the default is `mephisto/generators/form_composer/data` directory)
- `-v/--verify` - if truthy, validates all JSON configs currently present in the form builder config directory
- `-p/--permutate-sepatate-tokens` - if truthy, generates token sets values as all possible combinations of values of individual tokens
- `-f/--update-file-location-values S3_FOLDER_URL` - generates token values based on file names found within the specified S3 folder (see a separate section about this mode of running FormComposer)
- `-e/--extrapolate-token-sets` - if truthy, generates Task data config based on provided form config and takon sets values
- `-u/--use-presigned-urls` - a **modifier** for `--update-file-location-values` command that converts S3 URLs into short-lived rtemporary ones (for more detailes see "Presigned URLs" section)

To understand what the concept of "tokens" means, read on about FormComposer config structure.


## Config files

You will need to provide FormComposer with a JSON configuration of your form fields,
and place it in `generators/form-composer/data` directory.

- The task config file should be named `task_data.json`, and contain a list of JSON objects, each one with one key `form`.
- If you want to slightly vary your form within a Task (by inserting different values into its text), you need to add two files (that will be used to auto-generate `task_data.json` file):
    - `token_sets_values_config.json` containing a JSON array of objects (each with one key `tokens_values` and value representing name-value pairs for a set of text tokens to be used in one form version).
    - `form_config.json` containing a single JSON object with one key `form`.
- For more detail, read on about dynamic form configs.

For detailed structure of each config file, see [Config file reference](#config-file-reference).

Working config examples are provided in `examples/form_composer_demo/data` directory:
- task data config: `simple/task_data.json`
- form config: `dynamic/form_config.json`
- token sets values config: `dynamic/token_sets_values_config.json`
- separate tokens values: `dynamic/separate_token_values_config.json` to create `token_sets_values_config.json`
- resulting extrapolated config: `dynamic/task_data.json`


## Embedding FormComposer into custom application

A few tips if you wish to embed FormComposer in your custom application:

- to extrapolate form config (and generate the `task_data.json` file), call the extrapolator function `mephisto.generators.form_composer.configs_validation.extrapolated_config.create_extrapolated_config`
    - For a live example, you can explore the source code of [run_task_dynamic.py](/examples/form_composer_demo/run_task_dynamic.py) module


---


# Multiple form versions

The simplest Task scenario is showing the same exact form to all of your workers. In that case you need to:

- Compose `task_data.json` file containing definition of a single form (and place it into FormComposer config folder)
- Optionally, verify your config: `mephisto form_composer_config --verify`
- Run FormComposer: `mephisto form_composer`

But suppose you wish to show a slightly different version of the form to your workers. You can do so by defining multiple form versions. FormComposer provides several ways of doing so.

---

## Custom form versions

If your form versions vary considerably (e.g. showing different sets of fields), you should do the following steps:

- Populate these form versions into `task_data.json` file manually (it will be basically a JSON array of N individual form versions configs)
- Optionally, verify your config: `mephisto form_composer_config --verify`
- Run FormComposer: `mephisto form_composer`

_As a result, for each Task assignment Mephisto will automatically produce N units, each unit having a different form version. In total you will be collecting data from `N * units_per_assignment` workers._

---

## Dynamic form config

If your form versions vary only slightly (e.g. same set of fields, but showing different images or different text), you should use a dynamic form config as follows:

- Ensure you populate these files, and place them into your FormComposer config folder:
    - `form_config.json`: tokenized form config - same as regular form config, except it will contain tokens within certain objects' attributes (see [Tokens extrapolation](#tokens-extrapolation))
    - `token_sets_values_config.json`: file containing sets of token values, where each set is used to generate one version of the form (and each form version will be completed by `units_per_assignment` different workers).
- Optionally, verify your files: `mephisto form_composer_config --verify`
- Generate task data config: `mephisto form_composer_config --extrapolate-token-sets`
    - This will overwrite existing `task_data.json` file with auto-generated form versions, by extrapolating provided token sets values
- Run FormComposer: `mephisto form_composer`

_The number of generated form versions N will be same as number of provided token sets. In total you will be collecting data from `N * units_per_assignment` workers._

---

#### Tokens extrapolation

How does token extrapolation work?

A token is a named text placeholder that gets replaced ("extrapolated") by values specified in `token_sets_values_config.json` (each set of token values produces one form version based on dynamic form config `form_data.json`).

Token placeholders within an attribute are formatted like so: `{{TOKEN_NAME}}`

Tokens can be placed within the following object attributes:

- `help`
- `instruction`
- `label`
- `title`
- `tooltip`

If you wish to reuse the same token across different form attributes and levels, it's enough to specify it in a set of token values just once. (This also means that token names must be unique within token values sets)


---

#### Generate token sets with `--update-file-location-values`

In a special case when all of your tokens sets are simply permutations of several value lists, sets of token values can be easily auto-generated.

- Populate your lists of values for every separate token into `separate_token_values_config.json` file
- Optionally, verify your config: `mephisto form_composer_config --verify`
- Generate `token_sets_values_config.json` with command: `mephisto form_composer_config --permutate-separate-tokens`

_"Permutation" means all possible combinations of values. For example, permutations of amounts `2, 3`, sizes `big` and animals `cats, dogs` will produce result `2 big cats, 2 big dogs, 3 big cats, 3 big dogs`._

---

#### Generate separate token values with `--update-file-location-values`

In a special case when one of your tokens is an S3 file URL, that token values can be easily auto-generated.

- Make a public S3 folder that will contain only the files that you want (all of them)
- Run command: `mephisto form_composer --update-file-location-values S3_FOLDER_URL`
- As a result, a token with name `"file_location"` will be added to your `separate_token_values_config.json` config file. Its values will be S3 URLs of all files found .recursively within the `S3_FOLDER_URL`

---

#### Mturk Task Preview

For Tasks run with Mechanical Turk provider, FormComposer generates a Task preview (a small HTML snippet shown to worker prior to starting the task). This Task review comprises HTML content of `form` object's attributes `title` and `instruction`.

However, note that the task preview is inherently static, therefore:
- we always take the first form version in `data_task.json` to generate Task preview for all form versions
- we erase dynamic tokens from the Task review content

---

## Dynamic form config example

Putting it altogether, this is a brief example of composing a dynamic form config.

#### Separate token values config

Let's start with separate token values in `separate_token_values_config.json` file:

```json
{
  "actor": ["Carrie Fisher", "Mark Hamill"],
  "movie_name": ["Star Wars"]
}
```

#### Token values config

Permutating these token values will produce this `form_config.json` file with token sets values:

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
      "actor": "Mark Hamill",
      "movie_name": "Star Wars"
    }
  },
]
```

Example of config after using `--update-file-location-values "https://s3.amazonaws.com/...." --use_presigned_urls` params:
```json
[
  {
    "tokens_values": {
      "file_location": "{{getPresignedUrl(\"https://s3.amazonaws.com/1.jpg\")}}"
    }
  },
  {
    "tokens_values": {
      "file_location": "{{getPresignedUrl(\"https://s3.amazonaws.com/2.jpg\")}}"
    }
  },
]
```

#### Form config

These tokens are placed into the `form_config.json` dynamic form config like so:

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
  "instruction": "Rate the plot in movie '{{movie_name}}' out of 10",
  ...
}
```

#### Task data config

After extrapolating attributes from `form_config.json` with token sets from `token_sets_values_config.json`, we get the resulting `task_data.json` file used for the task:

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
  "instruction": "Rate the plot in movie 'Star Wars' out of 10?",
  ...
},
// Second extrapolated form version
{
  ...
  "instruction": "Rate Mark Hamill's performance in movie <b>'Star Wars'</b>",
  ...
  "help": "Please only consider the movie 'Star Wars'",
  ...
}
...
{
  ...
  "instruction": "Rate the plot in movie 'Star Wars' out of 10?",
  ...
}
```


---


# Custom field handlers

TBD

---


# Form callbacks

During rendering of a Task in the browser, we may send calls to the server-side for additional data. In Mephisto, API views servicing such requests are called "remote procedures".


## Presigned S3 URLs

An example of a remote procedure that gets called during the initial form loading, is `getPresignedUrl` and `getMultiplePresignedUrls` functions. These functions allow to generate short-lived S3 URLs, in order to limit exposure of sensitive resources.

The below command auto-generates config token values that presign themselves during rendering of the Task page:

```
mephisto form_composer_config --update-file-location-values "https://s3.amazonaws.com/..." --use_presigned_urls
```

This is how URL pre-signing works:
  - When a worker opens the Task page and the form HTML is generated, it will contain so-called "procedure tokens", i.e. token values that look like this: `{{getMultiplePresignedUrls(<S3_FILE_URL>)}}`
    - the "wrapper" part of a procedure token is the name of a Javascript function that will render itself dynamically (e.g. by calling some remote API to receive additional data)
    - the argument part is the argument value provided suring the function call
  - As soon as the form HTML is in place, the remote procedure gets called
  - Mephisto's predefined remote procedure generates presigned URL, and its expiration starts ticking

Presigned S3 URLs use the following environment variables:
  - Required: valid AWS credentials: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`
  form_composer_config` command)
  - Optional: URL expiration time `S3_URL_EXPIRATION_MINUTES` (if missing the default value is 60 minutes)


## Custom callbacks

You can write your own remote procedures. A good place to start is looking at how S3 URL presigning is implemented in the `examples/form_composer_demo` example project.

-----


# Config file reference

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
  },
  ...
]
```

#### Form config levels

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

_Note that, due to limitations of JSON format, HTML content needs to be converted into a single long string of text._


---

###### Config level: form

`form` is a top-level config object with the following attributes:

- `instruction` - HTML content describing this form; it is located before all contained sections (String, Optional)
- `title` - HTML header of the form (String)
- `submit_button` - Button to submit the whole form and thus finish a task (Object)
    - `instruction` - Text shown above the "Submit" button (String, Optional)
    - `text` - Label shown on the button (String)
    - `tooltip` - Browser tooltip shown on mouseover (String, Optional)
- `sections` - **List of containers** into which form content is divided, for convenience; each section has its own validation messages, and is collapsible (Array[Object])

---

###### Config level: section

Each item of `sections` list is an object with the following attributes:

- `collapsable` - Whether the section will toggle when its title is clicked (Boolean, Optional, Default: true)
- `initially_collapsed` - Whether the section display will initially be collapsed (Boolean, Optional, Default: false)
- `instruction` - HTML content describing this section; it is located before all contained fieldsets (String, Optional)
- `name` - Unique string that serves as object reference when using dynamic form config (String)
- `title` - Header of the section (String)
- `fieldsets` - **List of containers** into which form fields are grouped by meaning (Array[Object])

---

###### Config level: fieldset

Each item of `fieldsets` list is an object with the following attributes:

- `instruction` - HTML content describing this fieldset; it is located before all contained field rows (String, Optional)
- `title` - Header of the section (String)
- `rows` - **List of horizontal lines** into which section's form fields are organized (Array[Object])

---

###### Config level: row

Each item of `rows` list is an object with the following attributes:

- `fields` - **List of fields** that will be lined up into one horizontal line

---

###### Config level: field

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

######## Attributes - all fields

The most important attributes are: `label`, `name`, `type`, `validators`

- `help` - HTML explanation of the field/fieldset displayed in small font below the field (String, Optional)
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
    - `fileExtension`: Ensure uploaded file has specified extension(s) (e.g. `["doc", "pdf"]`) (Array<String>)
- `value` - Initial value of the field (String, Optional)


######## Attributes - select field

- `multiple` - Support selection of multiple provided options, not just one (Boolean. Default: false)
- `options` - list of available options to select from. Each option is an object with these attributes:
    - `label`: displayed text (String)
    - `value`: value sent to the server (String|Number|Boolean)


######## Attributes - checkbox and radio fields

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
      "actor": "Carrie Fisher",
      "movie_name": "Star Wars",
      "genre": "Sci-Fi"
    }
  },
  {
    "tokens_values": {
      "actor": "Keanu Reeves",
      "movie_name": "The Matrix",
      "genre": "Sci-Fi"
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
  "movie_name": ["Star Wars", "The Matrix"],
  "genre": ["Sci-Fi"]
}

```
