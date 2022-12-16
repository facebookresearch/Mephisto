---
sidebar_position: 4
---

import Link from '@docusaurus/Link';

# Check against standards with Gold Labels

Gold labeling is commonly used for ensuring worker quality over the full duration of a task. It's valuable as an automated measure to track the consistency your workers. For this Mephisto provides the `UseGoldUnit` blueprint mixin. 


## Basic configuration

There are a few primary configuration parts for using gold units:
- Hydra args
  - `blueprint.gold_qualification_base`: A string representing the base qualification that required qualifications keeping track of success will be built from.
  - `blueprint.use_golds`: Set to `True` to enable the feature.
  - `min_golds`: An int for the minimum number of golds a worker needs to complete for the first time before receiving real units.
  - `max_incorrect_golds`: An int for the number of golds a worker can get incorrect before being disqualified from this task.
- `GoldUnitSharedState`:
  - `get_gold_for_worker`: A factory that generates input data for a gold unit for a worker. Explained in-depth below.

With these set up, you'll also need to provide additional arguments to your `SharedTaskState` to register the required qualifications and the gold validation function. For example, your run script main may look something like like:
```python
...
gold_data: List[Dict[str, Any]] = ...
gold_ans = ...

def validate_gold_unit(unit: "Unit"):
    agent = unit.get_assigned_agent()
    data = agent.state.get_data()
    return data['outputs']['val'] == gold_ans[data['inputs']['ans_key']]

shared_state = SharedTaskState(
    ...
    get_gold_for_worker=get_gold_factory(gold_data)
    on_unit_submitted=UseGoldUnit.create_validation_function(cfg.mephisto, validate_gold_unit)
)
shared_state.qualifications += UseGoldUnit.get_mixin_qualifications(cfg.mephisto, shared_state)
...
```

### `get_gold_for_worker`

The core functionality to provide to your `SharedTaskState` to enable gold units is a `get_gold_for_worker` factory function which produces the input data that a worker should receive when Mephisto is giving them a gold unit.

We provide a helper `get_gold_factory` method which takes in a list of _all_ possible gold data inputs, and returns a factory that randomly selects a gold not yet completed by the given worker. This should be sufficient for most cases, though you can write your own factory if you want to be even more specific about how you assign golds.

## Advanced configuration

There are additional arguments that you can use for more advanced configuration of gold units:
There are a few primary configuration parts for using gold units:
- `GoldUnitSharedState`:
  - `worker_needs_gold`: A function that, given the counts of completed, correct, and incorrect golds for a given worker, as well as the minimum number of required golds, returns whether or not the worker should be shown a gold task. 
  - `worker_qualifies`: A function that, given the counts of completed, correct, and incorrect golds for a given worker, as well as the maximum number of incorrect, returns whether or not the worker is eligible to work on the task.

### `worker_needs_gold`

By default we use a logrithmic function that decreases the frequency of gold units as the worker successfully completes them, starting at the `min_golds` value of golds, then 1 gold in the first 10 units, ~%5 golds at 100 units, and ~1% golds at 1000 units.

If you want to do something more complicated, or use a different rate, you can override this for a custom scaling rate.

### `worker_qualifies`

By default we use a strikes system, where if the worker exceeds the `max_incorrect_golds` value we prevent them from working on more tasks. Depending on your acceptable level of noise (either in your gold labels, interpretation, or output dataset), you may instead want to base this on a fraction of incorrect golds to golds completed so far.

## Additional Questions?

You can find more information on using gold units in the reference documentation for <Link target={null} to="pathname:///python_api/mephisto/abstractions/blueprints/mixins/use_gold_unit.html">`UseGoldUnit`</Link>.
