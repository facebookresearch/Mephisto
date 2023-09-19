### Using Eligibility Requirements in configuring TaskRun

Prolific Eligibility Requirements are the equivalent of Mephisto Qualifications,
and are used to allow Participants to see our published Studies in Prolific.

To enable Participant filtering by custom Mephisto Qualifications
(i.e. not supported by Prolific), we create a one-time (dynamically updated) Participant Group
containing all known Participants filtered by those custom qualifications.
Then we pass ID of that Eligibility Participant Group (EPG) to Prolific API via
`ParticipantGroupEligibilityRequirement` Study requirement. After Study concludes, this
disposable EPG is removed.

NOTE: If you use several Eligibility Requirements together (e.g.
`CustomBlacklistEligibilityRequirement`, `CustomWhitelistEligibilityRequirement`, and
`ParticipantGroupEligibilityRequirement`), then Participants will be selected by
intersecting all of these requirements.


-------------------------------------------------------------------------------
#### Usage

Shared state handles both custom and Prolific-supported qualifications:

```python
shared_state.prolific_specific_qualifications = [
    {
        'name': 'AgeRangeEligibilityRequirement',
        'min_age': 18,
        'max_age': 100,
    },
]

shared_state.qualifications = [
    make_qualification_dict('sample_qual_name', QUAL_GREATER_EQUAL, 1),
]
```

You can alternatively indicate Prolific-supported requirements in Hydra YAML config
under the key `prolific_eligibility_requirements` like so:

```yaml
mephisto:
  provider:
    prolific_eligibility_requirements:
      - name: 'AgeRangeEligibilityRequirement'
        min_age: 10
        max_age: 20
```



-------------------------------------------------------------------------------
#### Available Eligibility Requirements

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



-------------------------------------------------------------------------------
#### Block lists and Allow lists

Currently we're not using Participant Groups called `prolific_allow_list_group_name`
and `prolific_block_list_group_name` for anything (even though we diligently maintain them
via Prolific's API).

- Manual allow list is applied via `CustomWhitelistEligibilityRequirement`
- Manual block list is applied via `CustomBlacklistEligibilityRequirement`.
- Automatic block list is applied by not including ineligible Participants into EPG
as per `is_blocked` column in the prolific datastore table.



-------------------------------------------------------------------------------
### Prolific API oddities

#### Statuses

Prolific lacks several important statuses for Studies:

- `EXPIRED` status: we simulate it with adding a special suffix to `Study.internal_name`.
- `STOPPED` status: whether Study has naturally completed,
or it was manually stopped via Prolific UI, in both cases it will transition to `AWAITING_REVIEW`
status.
- `FINISHED` status: all `COMPLETED` and `AWAITING_REVIEW` studies in Prolific are not really
completed - they can still be reactivated by increasing their `total_available_places` parameter.

You may also bump against some unobvious behaviours of Prolific Studies:

1. We cannot stop Study via Prolific UI when `max_num_concurrent_units` is specified,
because Mephisto will keep on launching additional Units (and thus reactivating the Study)
every time Study falls into `AWAITING_REVIEW` status, until all created Units have been launched.
2. When we use `max_num_concurrent_units`, every time available places drop to zero for a moment,
Prolific will automatically transition Study into `AWAITING_REVIEW` status,
as if the Study has already finished.
3. Every time Prolific is updating status of a Study or Submission, it briefly puts that object
status to an undocumented `PROCESSING` status.



-------------------------------------------------------------------------------
#### Studies/Submissions

1. When Prolific Study is created with `ParticipantGroupEligibilityRequirement`,
Prolific UI doesn't show it under `Study.eligibility_requirements` - it's only
visible via an API request. (And `id` in that Eligibility Requirement will be
not the EPG ID, but rather some internal ID from Prolific DB.)
2. After Study has been publiched, Prolific only allows updating `internal_name` and
`total_available_places` (all other fields are read-only, including Allow List and Block List).
This is the reason we're using disposable EPGs for every Study.
3. Prolific only allows increasing (but not decreasing) `total_available_places`
4. The way to set Submission as completed is not by issuing an API call, but by redirecting
a Participant in their browser to a page with a specific URL that includes a Study completion code.
5. Prolific does not allow to specify custom Study completion code during creation of a Study,
therefore we have to generate our own completion codes based on Study's ID and
update it in Prolific when creating a Study.



-------------------------------------------------------------------------------
#### Groups

1. Prolific caches `eligible_participant_count` for Groups (so it always shows the initial value,
despite any changes of Particpants in the Group)
2. Deletion of Participant Groups is soft on Prolific side, and their API response doesn't
indicate that a Group has been soft-deleted (as if it's still active)



-------------------------------------------------------------------------------
### Steps of running a Study

1. Create inactive Study during TaskRun launch, set its `total_available_places = None`.
(Mephisto will create all required units with `created` status.)
2. Update Study with generated `completion_codes` (we need `Study.id` for it).
3. Publish the Study on Prolific.
4. When Mephisto launches a new Unit, increase `total_available_places` in Prolific Study.
5. When a Unit is expired (i.e. completed or returned), Mephisto launches another Unit.
6. When all Units are expired, the Study is considered completed.
7. The results are reviewed by a user. (All currently active EPGs are dynamically changed,
based on workers' updated custom qualifications.)
