---
sidebar_position: 3
---

import Link from '@docusaurus/Link';

# Check worker quality with Screening Units

Screening units help filter out low-quality work, generally by hiding parts of the validation you're paying attention to behind the Mephisto server. To support this we provide the `ScreenTaskRequired` blueprint mixin.

Screening units are a heuristic-based way to determine, on the first task completion, if a worker has understood the instructions of a task. They can be run either on real data you want annotated (for cases where your heuristics can be run whenever) or on specific 'test' data you believe it's easier to validate on.


## Basic configuration

There are a few primary configuration parts for using screening units:
- Hydra args
  - `blueprint.passed_qualification_name`: A string qualification to mark people who have passed screening. Those who fail will be assigned `blueprint.block_qualification`.
  - `blueprint.use_screening_task`: Set to `True` to enable the feature.
  - `max_screening_units`: An int for the maximum number of screening tasks you're willing to launch with this batch. Used to limit how much you will pay out for units that aren't annotating your desired data.
- `ScreenTaskSharedState`:
  - `screening_data_factory`: `False` if you want to validate on real data. Otherwise, a factory that generates input data for a screening unit for a worker. Explained in-depth below.

With these set up, you'll also need to provide additional arguments to your `SharedTaskState` to register the required qualifications and the gold validation function. For example, your run script main may look something like like:
```python
...

def validate_screening_unit(unit: "Unit"):
    agent = unit.get_assigned_agent()
    data = agent.state.get_data()
    return my_heuristic_validation(data['outputs'])

shared_state = SharedTaskState(
    ...
    screening_data_factory=False
    on_unit_submitted=UseGoldUnit.create_validation_function(cfg.mephisto, validate_gold_unit)
)
shared_state.qualifications += UseGoldUnit.get_mixin_qualifications(cfg.mephisto, shared_state)
...
```

### `screening_data_factory`

The core functionality to provide to your `SharedTaskState` to enable screening units to run on test data before moving to the real data you want annotated. If you want to validate using heuristics on your real data, you can set this to `False`.

These should take the form of a generator that returns an object of `Dict[str, Any]` which will be used to populate the screening Unit's data. The most basic example would be:
```python
def my_screening_unit_generator():
    while True:
        yield {'task_data': 'some screening data', 'is_screen': True}
```

## Additional Questions?

You can find more information on using screening units in the reference documentation for <Link target={null} to="pathname:///python_api/mephisto/abstractions/blueprints/mixins/screen_task_required.html">`ScreenTaskRequired`</Link>.
