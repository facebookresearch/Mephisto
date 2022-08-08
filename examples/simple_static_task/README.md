# Simple Static Task
This example script is to demonstrate how to launch a simple task using a html file. The "static" nature of this task means that all of the content required for a worker to complete the task must be set before the task is launched, and must be able to be sent to the app upon initialization.

This specific example can be run with:
```console
python static_test_script.py
```

and can additionally be launched with an onboarding step by specifying an onboarding qualification:

```console
python static_run_with_onboarding.py
```

## Submit button customization
### Hide the submit button 
Writing the markup below in `demo_task.html` will allow you to hide the submit button.

```html
<script>
  window._MEPHISTO_CONFIG_.set("HIDE_SUBMIT_BUTTON", true)
</script>
```

You can get window properties as such:
```html
<script>
  window._MEPHISTO_CONFIG_.get("HIDE_SUBMIT_BUTTON")
</script>
```


## Testing
To run tests locally you should first launch the task as follows:

```bash
python static_test_script.py
```
This will run the task.

Then go into the `mephisto/abstractions/blueprints/static_html_task/source` and run 
```console
npm run test
``` 
to open cypress.

Select the Chrome browser and click on the one spec that shows up to run the tests.
