# Qualifications
Qualification control is a powerful component of Mephisto, allowing you to filter out workers with both manual and automatic controls. Within this are typical allowlists and blocklists, setting up value-based qualifications, making automatic qualifications for onboarding, and also utilizing the qualifications that various crowdsourcing providers have to offer. This document seeks to describe some common use cases for qualifications, and how we currently go about using them.


# Blocking qualifications
When you set a `blocking_qualification` during a launch, calling `Worker.grant_qualification(<blocking_qualification>)` will prevent that worker from working on any tasks that you have set the same `blocking_qualification` for. You can use this to set up blocklists for specific tasks, or for groups of tasks.

# Onboarding qualifications
Mephisto has an automatic setup for assigning workers qualifications for particular tasks that they've worked on, such that it's possible to specify a qualification that a worker can be granted on the first time they take out a particular task. This qualification is given the name `onboarding_qualification`, and is compatible with any blueprints that have onboarding tasks.

When a worker accepts your task for the first time, they will have neither the passing or failing version of the onboarding qualification, and will be put into a test version of the task that determines if they are qualified. Then only those that qualify the first time will be able to continue working on that task.

The `onboarding_qualification` is shared between all task runs that use the same qualification name, and as such you can ensure that a worker need not repeatedly qualify for the same or similar tasks by sharing the same lists.

You can also set up tasks that are only available to workers that have passed an existing onboarding (potentially for tasks that don't have their own onboarding), or use the onboarding failure list as a block list for a future task. Both examples are shown below:

```python
from mephisto.abstractions.blueprints.mixins.onboarding_required import OnboardingRequired
from mephisto.data_model.qualification import QUAL_EQUAL, QUAL_NOT_EXIST, make_qualification_dict

ONBOARDING_QUALIFICATION_NAME = "TEST_ONBOARDING_QUAL_NAME"

# Making a qualification that requires a worker has 
# passed an onboarding from a different task
shared_state.qualifications = [
    make_qualification_dict(
        ONBOARDING_QUALIFICATION_NAME,
        QUAL_EQUAL,
        1,
    )
]

# Making a qualification that requires that a worker 
# has not failed a particular onboarding from a different task
shared_state.qualifications = [
    make_qualification_dict(
        OnboardingRequired.get_failed_qual(ONBOARDING_QUALIFICATION_NAME),
        QUAL_NOT_EXIST,
    )
]
```

# Allowlists and Blocklists
Similarly to how the standard `blocking_qualification` works, it's possible to add additional qualifications to `Worker`s by granting workers qualifications and making their existence exclusive or inclusive. This is accomplished by adding the qualifications to your `SharedTaskState`:
```python
from mephisto.data_model.qualification import QUAL_NOT_EXIST, make_qualification_dict

# Qualifications
ALLOWLIST_QUALIFICATION = "some_allowlist_qual"
BLOCKLIST_QUALIFICATION = "some_blocklist_qual"

# ... potentially in some other script
w = unit.get_assigned_agent().get_worker()
# worker did well
w.grant_qualfication(ALLOWLIST_QUALIFICATION)
# worker did not do well
w.grant_qualification(BLOCKLIST_QUALIFICATION)

# ... when launching a task
shared_state.qualifications = [
    make_qualification_dict(
        ALLOWLIST_QUALIFICATION,
        QUAL_EXISTS,
    ),
    make_qualification_dict(
        BLOCKLIST_QUALIFICATION,
        QUAL_NOT_EXISTS,
    ),
]
```

# Adding custom qualifications to SharedTaskState
You should be able to specify a qualification in Mephisto using the following:
```python
from mephisto.operations.utils import find_or_create_qualification

find_or_create_qualification(db, "MY_QUALIFICATION_NAME")
```
This will create a local Mephisto registration for the given qualification by name. Later on if you try to use this qualification with a crowd provider (like MTurk), it'll go through the process of making sure it's registered with them properly for you. So then later on you can do:
```python
from mephisto.data_model.qualification import make_qualification_dict
...
shared_state.qualifications = [
    make_qualification_dict(
        "MY_QUALIFICATION_NAME", QUAL_COMPARATOR, QUAL_VALUE
    )
]
```
where `QUAL_COMPARATOR` is any of the comparators available [here](https://github.com/facebookresearch/Mephisto/blob/9ca7534696eeab9ddb8ead06b110125b91789baf/mephisto/data_model/qualification.py#L21-L30) in the Qualification module and `QUAL_VALUE` is the desired value of that qualification (must be `None` for `QUAL_EXISTS` and `QUAL_NOT_EXIST`).

You can directly grant that qualification to mephisto `Worker`'s using `Worker.grant_qualification("QUALIFICATION_NAME", qualification_value)`.

# What if I want to block a worker that hasn't connected before?
For this you'll want to use the interface that a `CrowdProvider` has set up to do the granting process directly. An example for this can be found in `abstractions.providers.mturk.utils.script_utils`. 

Note, while you're able to grant these qualifications to a worker that isn't tracked by Mephisto, it will not be possible for Mephisto to help in bookkeeping qualifications granted to workers in this manner.

# What if I want to use qualifications only set by a provider?
For the special case of provider-specific qualifications, `SharedTaskState` has fields for `<provider>_specific_qualifications` wherein you can put qualifications in the expected format for that crowd provider. For instance, you can do the following for using an MTurk-specific qualification on a task:
```python
shared_state = #... initialize a SharedTaskState for your run

shared_state.mturk_specific_qualifications = [
    {
         "QualificationTypeId": "00000000000000000040",
         "Comparator": "GreaterThanOrEqualTo",
         "IntegerValues": [1000],
         "ActionsGuarded": "DiscoverPreviewAndAccept",
    },
]
```