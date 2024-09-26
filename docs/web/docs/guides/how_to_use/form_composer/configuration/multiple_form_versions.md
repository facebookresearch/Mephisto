---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# Multiple form versions

The simplest Task scenario is showing the same exact form to all of your workers. In that case you need to:

- Compose `task_data.json` file containing definition of a single form (and place it into FormComposer config folder)
- Optionally, verify your config: `mephisto form_composer config --verify`
- Run FormComposer: `mephisto form_composer`

But suppose you wish to show a slightly different version of the form to your workers. You can do so by defining multiple form versions. FormComposer provides several ways of doing so.

---

## Custom form versions

If your form versions vary considerably (e.g. showing different sets of fields), you should do the following steps:

- Populate these form versions into `task_data.json` file manually (it will be basically a JSON array of N individual form versions configs)
- Optionally, verify your config: `mephisto form_composer config --verify`
- Run FormComposer: `mephisto form_composer`

_As a result, for each Task assignment Mephisto will automatically produce N units, each unit having a different form version. In total you will be collecting data from `N * units_per_assignment` workers._

---

## Dynamic form config

If your form versions vary only slightly (e.g. same set of fields, but showing different images or different text), you should use a dynamic form config as follows:

- Ensure you populate these files, and place them into your FormComposer config folder:
    - `unit_config.json`: tokenized form config - same as regular form config, except it will contain tokens within certain objects' attributes (see [Tokens extrapolation](#tokens-extrapolation))
    - `token_sets_values_config.json`: file containing sets of token values, where each set is used to generate one version of the form (and each form version will be completed by `units_per_assignment` different workers).
- Optionally, verify your files: `mephisto form_composer config --verify`
- Generate task data config: `mephisto form_composer config --extrapolate-token-sets`
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
- Optionally, verify your config: `mephisto form_composer config --verify`
- Generate `token_sets_values_config.json` with command: `mephisto form_composer config --permutate-separate-tokens`

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

Permutating these token values will produce this `unit_config.json` file with token sets values:

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

#### Unit config

These tokens are placed into the `unit_config.json` dynamic form config like so:

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

After extrapolating attributes from `unit_config.json` with token sets from `token_sets_values_config.json`, we get the resulting `task_data.json` file used for the task:

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
