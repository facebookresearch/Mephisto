### Using Eligibility Requirements in configuring TaskRun

List of supported Eligibility Requirements for `SharedState.prolific_specific_qualifications`:

```python
[
    {
        'name': 'AgeRangeEligibilityRequirement',
        'min_age': '<value>',
        'max_age': '<value>',
    },
    {
        'name': 'ApprovalNumbersEligibilityRequirement',
        'minimum_approvals': '<value>',
        'maximum_approvals': '<value>',
    },
    {
        'name': 'ApprovalRateEligibilityRequirement',
        'minimum_approval_rate': '<value>',
        'maximum_approval_rate': '<value>',
    },
    {
        'name': 'CustomBlacklistEligibilityRequirement',
        'black_list': '<value>',
    },
    {
        'name': 'CustomWhitelistEligibilityRequirement',
        'white_list': '<value>',
    },
    {
        'name': 'JoinedBeforeEligibilityRequirement',
        'joined_before': '<value>',
    },
    {
        'name': 'ParticipantGroupEligibilityRequirement',
        'id': '<value>',
    },
]
```

_NOTE: this list (last updated 2023.07.11) is derived from list of available classes
in `mephisto/abstractions/providers/prolific/api/eligibility_requirement_classes`._

You can use these requirements in Hydra YAML config under the key
`prolific_eligibility_requirements` like so:

```yaml
mephisto:
  provider:
    prolific_eligibility_requirements:
      - name: 'AgeRangeEligibilityRequirement'
        min_age: 10
        max_age: 20
```
