---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 4
---

# Prolific API oddities

_Last updated 2023.07.08_ <br/>
_Prolific doesn't publish API releases and release notes, so these could've already been fixed_

## Statuses

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

---

## Studies/Submissions

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

---

## Groups

1. Prolific caches `eligible_participant_count` for Groups (so it always shows the initial value,
despite any changes of Particpants in the Group)
2. Deletion of Participant Groups is soft on Prolific side, and their API response doesn't
indicate that a Group has been soft-deleted (as if it's still active)
