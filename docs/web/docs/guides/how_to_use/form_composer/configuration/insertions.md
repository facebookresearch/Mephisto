---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 7
---

# Using code insertions

FormComposer allows using custom code insertions in these scenarios:
- Specify lengthy content of an attribute (e.g. "instruction") in a separate HTML file
- Define custom validators for form fileds in a JS file
- Define custom triggers for form fileds, sections and submit button in a JS file
- Define custom styles for the FormComposer UI in a CSS file

The inserted code must reside in separate files (called "insertion files") located in `insertions` subdirectory of your form config directory.
- _Remember that you can change default config directory path using `--directory` option of `form_composer config` command_

---

## HTML content insertion

An HTML insertion file is specified as a file path that's relative to the form config. It can be inserted directly into `unit_config.json` config, or via a token.

#### Insertion without token

Simply set entire value of an attribute to the insertion file's path.
This is equivalent to setting value of that attribute to content of the HTML file (except now you don't have to stitch all HTML content into a single unreadable JSON line).

Attributes that support HTML insertions are the same ones that support tokens

Example in `unit_config.json`:
```json
{
  ...
  "instruction": "insertions/some_content.html"
  ...
}
```

#### Insertion via token

Use an extrapolated token as usual, and set that token's value to the insertion file's path.
Upon extrapolation, value of such token will be automatically replaced with content of the HTML file.

Example in `token_sets_values_config.json`:
```json
[
  {
    "tokens_values": {
      "some_long_content": "insertions/long_content.html"
    }
  }
]
```

Then embed this token into `unit_config.json`:
```json
{
  ...
  "instruction": "Please see the below instructions: {{some_long_content}}"
  ...
}
```


## JS validator insertion

You can define your own custom field validator as a Javascript function, and place it in a special file `insertions/custom_validators.js` inside your form config directory.
When a Task is rendered in the browser, your validator function (let's call it `myValidator`) will be imported from this file.

In form config, the validator function is associated with a field by adding this key-value pair under "validators" attribute:
```json
"myValidator": myValidatorArgument
```

In your custom code, each validator function must have the following signature:
- Accept 2 required arguments `field` and `value`, and extra arguments as needed
    - `field` is a JS object representing a rendered form field
    - `value` is provided value of the field (format depends on the field type)
    - Extra arguments will be passed after the `value` argument (they come from the `myValidatorArgument` value you specified in the form config under `"myValidator"` key) :
        - If the value is a non-Array (Boolean, String, Number, or non-array Object), it will be passed as-is
        - If the value is an Array, the content of Array will be decostructed and passed as separate positional arguments.
- Return value must be either:
    - `null` if validation passed successfully
    - String if validation failed
        - This value will be shown to user as an error message underneath the field, and in the error summary block

Example in `custom_validators.js`...

```js
// You can import some functions from another file
import { someHelper } from "./helpers.js";

export function fieldContainsWord(field, value, word) {
  someHelper();

  if (value.includes(word)) {
    return null;
  }

  return `Field ${field.name} must contain a word "${word}".`;
}

// This way you can separate all your validators into separate files, for convenience
export { phoneValidatorFunction } from "./phone_validator_code.js";
```

...and its usage in `unit_config.json`:
```json
{
  ...
  "validators": {
    "required": true,
    ...
    "fieldContainsWord": "Mephisto"
  },
  ...
}
```

## JS trigger insertion

You can define your own custom trigger for a specific form element as a Javascript function, and place it in a special file `insertions/custom_triggers.js` inside your form config directory.
When a Task is rendered in the browser, your validator function (let's call it `myTrigger`) will be imported from this file.
NOTE: triggers are called synchronously in the current implementation and your code inside trigger funtion must be synchronous too.

In form config, the trigger function is associated with an element by adding this key-value pair under "triggers" attribute:
```json
"myTrigger": [myTriggerEventType, myTriggerArgument]
```

In your custom code, each trigger function must have the following signature:
- Accept 4 required arguments `formData`, `updateFormData`, `element`, `fieldValue`, `formFields`, and extra arguments as needed
    - `formData` is a React state with form data (`{<fieldName>: <fieldValue>, ...}`)
        - This allows to lookup values of any form field by its `"name"` attribute
    - `updateFormData` is a callback that sets value of any form field in the React state
        - This allows to change values of any form field by its `"name"` attribute, e.g. `updateFormData("name_first", "Austin")`. Note that you will need change HTML-field value as well.
    - `element` is the form object that fired the trigger (i.e. "field", "section" or "submit button" object defined in form config)
    - `fieldValue` is the value of an element that fired the trigger, if it's a form field (otherwise it's null)
    - `formFields` is an object containing all form fields as defined in 'unit_config.json' (otherwise it's null)
    - Extra arguments will be passed after the `fieldValue` argument (they come from the `myTriggerArgument` value you specified in the form config under `"myTrigger"` key) :
        - If the value is a non-Array (Boolean, String, Number, or non-array Object), it will be passed as-is
        - If the value is an Array, the content of Array will be decostructed and passed as separate positional arguments.

The `myTriggerEventType` parameter can take one of the following values, depending on the type of trigger element:
- non-field elements:
  - `"onClick"`
- "field" element:
  - `checkbox` field type:
      - `"onChange"`
      - `"onClick"` (triggered from any part of the entire field, not just the buttons)
  - `file` field type:
      - `"onChange"`
      - `"onBlur"`
      - `"onFocus"`
      - `"onClick"`
  - `input` field type:
      - `"onChange"`
      - `"onBlur"`
      - `"onFocus"`
      - `"onClick"`
  - `radio` field type:
      - `"onChange"`
      - `"onClick"` (triggered from any part of the entire field, not just the buttons)
  - `select` field type:
      - `"onChange"`
  - `textarea` field type:
      - `"onChange"`
      - `"onBlur"`
      - `"onFocus"`
      - `"onClick"`


Example in `custom_triggers.js`...

```js
export function onClickSectionHeader(
  formData, // React state for the entire form
  updateFormData, // callback to set the React state
  element, // "field", "section", or "submit button" element that invoked this trigger
  fieldValue, // (optional) current field value, if the `element` is a form field
  formFields, // (optional) Object containing all form fields as defined in 'unit_config.json'
  sectionName // Argument for this trigger (taken from form config)
) {
  alert(`${sectionName} section was clicked!`);
}
```

...and its usage in `unit_config.json`:
```json
{
  ...,
  "triggers": {
    "onChange": ["onChangeName", [true, {"prefix": "_"}, 100]]
  }
  ...
  "triggers": {
    "onClick": ["onClickSectionHeader", "Triggerable"]
  }
  ...
}
```

#### JS trigger helpers

During development of your form config, you can use a few available helper functions.

1. `validateFieldValue` - checks whether you're assigning a valid value to a field
(in case you want to change them programmatically).

  Example of use:

  1. Add `mephisto-task-addons` in webpack config

  ```js
  resolve: {
    alias: {
      ...
      "mephisto-task-addons": path.resolve(
        __dirname,
        "<relativePath>/packages/mephisto-task-addons"
      ),
    },
  }
  ```
  2. Add import
  ```js
  import { validateFieldValue } from "mephisto-task-addons";
  ```
  3. Validate a value before assigning it to form field
  ```js
  const valueIsValid = validateFieldValue(formFields.languageRadioSelector, {"en": true, "fr": false}, true);
  ```

## CSS styles insertions

To customize UI appearance, and separate CSS styles from your HTML insertions,
you can create multiple CSS files in the `insertions` directory.
The only naming requirement is that their filenames should end with `.css` extension.
These CSS files will be automatically included in FormComposer UI via webpack build.

You can use CSS insertions to customize not only your HTML insertions pieces,
but also the standard Bootstrap form components themselves. There's two ways to do so:

- override existing styles (use CSS selectors for existing classes, names, ids, etc)
- add your own styles, and link them to ids and classes of form components (via their `id` and `classes` config attributes - see [Config files reference](/docs/guides/how_to_use/form_composer/configuration/config_files/))
