---
sidebar_position: 2
---

import Link from '@docusaurus/Link';

# Teach potential workers with Onboarding

The first step to getting quality data is describing your task properly and ensuring that workers have understood your instructions. To this end, Mephisto provides the `OnboardingRequired` Blueprint mixin.

Onboarding is an opportunity to give workers complete context of your task the first time they work on it. You can also use it to provide workers with a simple test to ensure they read and understand task instructions.

Mephisto's onboarding disqualifies workers that fail the test, so it's good practice to ensure that the tests should be completable by anyone who reads through the instructions and also don't take up too much time.

If you're instead interested in filtering out workers who don't hit a specific quality bar, refer to [using screening units](../using_screen_units), as Mephisto doesn't pay out for failed onboarding.


## Basic configuration

There are a few primary configuration parts for using onboarding units:
- Hydra args
  - `blueprint.onboarding_qualification`: A string qualification to mark a worker's onboarding status. Workers without this qualification will be shown the onboarding, and Mephisto will either grant a positive or negative value for this qualification to all workers that complete onboarding. Setting this to `None` disables onboarding.
- `OnboardingSharedState`:
  - `onboarding_data`: `Dict[str, Any]` of data you would like to populate the onboarding task's 
  - `validate_onboarding`: A function that takes the data returned by your onboarding task's `handleSubmit` and returns a bool for if the worker passed the onboarding.

For an example, your run script main using onboarding may look something like like:
```python
...

def validate_onboarding_data(onboarding_data):
    return onboarding_data['key_val'] == SOMETHING_CORRECT

shared_state = SharedTaskState(
    ...
    onboarding_data={'some_test_key': 'some_test_value'}
    validate_onboarding=validate_onboarding_data,
)
...
```

Unlike Screening and Gold units, Onboarding expects that you set up a custom frontend compared to your main task. You want to provide workers with an in-depth exploration of your task up-front (though you can always re-use onboarding components in your main task as reference materials). For more info on how to build out onboarding frontends, check out our [tutorial](../../../tutorials/worker_controls).

**Note:** We've observed that some workers may share out the answers for onboarding tasks, so we encourage that you make your validation questions configurable such that you can update them with a change to `onboarding_data`.

## Additional Questions?

You can find more information on using onboarding before your units in the reference documentation for <Link target={null} to="pathname:///python_api/mephisto/abstractions/blueprints/mixins/onboarding_required.html">`OnboardingRequired`</Link>.
