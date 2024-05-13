---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 3
---

# Participant Eligibility Requirements

Prolific offers Eligibility Requirements to limit access to your Task (or Study, as Prolific calls it)
to fitting Participants only.
These are similar to Mephisto's qualifications, except they exist in Prolific's cloud, not your local Mephisto DB.
This can be helpful in the beginning, when you're still building a pool of locally saved known workers.

As a technicality, filtering by Mephisto's Qualifications in Prolific is accomplished
via creating a disposable (and dynamically updated) Eligible Participant Group (EGP) on Prolific, that
contains all known workers satisfying Mephisto qualifications.
Mephisto automatically generates and passes that EGP id to Prolific
(as a `ParticipantGroupEligibilityRequirement` Study requirement),
and when Task is complete, Mephisto deletes that EPG.

When usingseveral Eligibility Requirements together (e.g.
`CustomBlacklistEligibilityRequirement`, `CustomWhitelistEligibilityRequirement`, and
Mephisto qualifications), then Participants will be selected by
intersecting all of these requirements.

---

## Usage

You can specify Prolific qualifications via Task config file, or directly in TaskRun shared state.

### Usage in shared state

Shared state can handle Prolific-supported qualifications. Example in `run_task.py`:

```python
shared_state.prolific_specific_qualifications = [
    {
        "name": "AgeRangeEligibilityRequirement",
        "min_age": 18,
        "max_age": 100,
    },
]

shared_state.qualifications = [
    make_qualification_dict("sample_qual_name", QUAL_GREATER_EQUAL, 1),
]
```

### Usage in task config

Prolific-supported requirements can be specified in Hydra YAML Task config file,
under the key `prolific_eligibility_requirements`:

```yaml
mephisto:
  provider:
    prolific_eligibility_requirements:
      - name: "AgeRangeEligibilityRequirement"
        min_age: 10
        max_age: 20
```

---

## Supported Eligibility Requirements

Mephisto currently supports the following Eligibility Requirements
under `SharedState.prolific_specific_qualifications`:

```python
[
    {
        "name": "AgeRangeEligibilityRequirement",
        "min_age": "<value>",
        "max_age": "<value>",
    },
    {
        "name": "ApprovalNumbersEligibilityRequirement",
        "minimum_approvals": "<value>",
        "maximum_approvals": "<value>",
    },
    {
        "name": "ApprovalRateEligibilityRequirement",
        "minimum_approval_rate": "<value>",
        "maximum_approval_rate": "<value>",
    },
    {
        "name": "CustomBlacklistEligibilityRequirement",
        "black_list": "<value>",
    },
    {
        "name": "CustomWhitelistEligibilityRequirement",
        "white_list": "<value>",
    },
    {
        "name": "JoinedBeforeEligibilityRequirement",
        "joined_before": "<value>",
    },
    {
        "name": "ParticipantGroupEligibilityRequirement",
        "id": "<value>",
    },
]
```

_NOTE: this list (last updated 2023.07.11) is derived from list of available classes
in `mephisto/abstractions/providers/prolific/api/eligibility_requirement_classes`._

---

## Block and Allow lists

Prolific provides a way to limit Study participants based on their IDs
via EGPs called `prolific_allow_list_group_name`
and `prolific_block_list_group_name`:

- Manual allow list is applied via `CustomWhitelistEligibilityRequirement`
    - This can be useful when testing your Task, and limiting its visibility to only a few test workers
- Manual block list is applied via `CustomBlacklistEligibilityRequirement`
    - We do not recommend using manual block list directly, because we auto-compose it during every TaskRun,
based on `is_blocked` column in the local datastore.
