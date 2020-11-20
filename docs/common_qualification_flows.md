# Qualifications
Qualification control is a powerful component of Mephisto, allowing you to filter out workers based on typical allowlists and blocklists, alongside other value based qualifications, while also utilizing the qualifications that various crowdsourcing providers have to offer. This document seeks to describe some common use cases for qualifications, and how we currently go about using them


# Blocking qualifications
But onboarding_qualification and block_qualifications can be used across tasks with the same, or different task names, or really anywhere.

# Onboarding qualifications
So if on a particular task you've used:
onboarding_qualification: "WORKER_HAS_PASSED_ONBOARDING"
you can reuse this qualification for other tasks.

you can directly do things like:
shared_state.qualifications = [
    make_qualification_dict(
        allowlist_qualification,
        QUAL_EQUAL,
        1,
    )
]

# Allowlists and Blocklists

# Custom qualifications
Sorry for the delay here! So you should be able to specify a qualification like:
from mephisto.operations.utils import find_or_create_qualification

find_or_create_qualification(db, "MY_QUALIFICATION_NAME")
This will create a local Mephisto registration for the given qualification. Later on if you try to use this qualification with a crowd provider (like MTurk), it'll go through the process of making sure it's registered with them properly for you. So then later on you can do:
from mephisto.data_model.qualification import make_qualification_dict
...
shared_state.qualifications = [
    make_qualification_dict(
        "MY_QUALIFICATION_NAME", QUAL_COMPARATOR, QUAL_VALUE
    )
]
where QUAL_COMPARATOR is any of the comparators available here:
https://github.com/facebookresearch/Mephisto/blob/9ca7534696eeab9ddb8ead06b110125b91789baf/mephisto/data_model/qualification.py#L21-L30
and QUAL_VALUE is the desired value of that qualification (must be None for QUAL_EXISTS and QUAL_NOT_EXIST).

You can directly grant that qualification to mephisto Worker's using Worker.grant_qualification("QUALIFICATION_NAME", qualification_value)

# What if I want to block a worker that hasn't connected before?
You can also directly assign the value 1 to a worker by their MTurk id by using the direct_soft_block_mturk_workers method in mephisto.abstractions.providers.mturk.utils.script_utils. It's not really designed for providing positive qualifications (and hence it just gives the value 1 to all of the workers), and it also doesn't record the qualification has been granted on the Mephisto side (and as such we won't be able to help with bookkeeping what worker has what qualification), but it can be useful if you need to do this.

# What if I want to use qualifications only set by a provider?
Ah rather than putting it while you init, you can just add it as a property afterwards.
shared_state = ...
shared_state.mturk_specific_qualifications = ...

"sandbox_block": {
    "QualificationTypeId": "3F9BH0EJUSTSHPUFR57BOW6LPKLKMM",
    "Comparator": "Exists",
    "ActionsGuarded": "DiscoverPreviewAndAccept",
}

t's possible overall to be using an existing qualification on MTurk just via the qualification id they provide, but I don't think it's as clean code-wise.
shared_state.mturk_specific_qualifications = [
    {
         "QualificationTypeId": "00000000000000000040",
         "Comparator": "GreaterThanOrEqualTo",
         "IntegerValues": [1000],
         "ActionsGuarded": "DiscoverPreviewAndAccept",
    },
]