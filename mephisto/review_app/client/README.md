<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# TaskReview app user flow

- We get list of available tasks from `GET /tasks`
- User selects a task
- We get list of available qualifications from `GET /qualifications`
- We pull all unit-worker id pairs from  `GET /tasks/{id}/worker-units-ids`
	  - *Due to the need to randomly shuffle units grouped by a worker (to mitigate reviewers bias, etc) we're implementing client-side pagination - client gets full list of all ids, creates a page of unit ids, and then pulls data for those specific units.*
- We initiate units review by worker:
    - Group units by worker
    - Sort workers by number of their units fewest units go first)
    - Pick them for review one-by-one
- For each worker:
    - We pull units by ids from `GET /units?unit_ids=[...]`
    - We sort units by `creation_date` and pick them for review one-by-one
        - For each reviewed unit:
            - We pull unit details from `GET /units/details?unit_ids=[...]`
            - We pull current stats from `GET /stats` (for entire task and for worker within the task)
            - We render unit's review representation in an iframe
            - User can choose to reject/accept unit, grant/revoke qualification, and block the worker
- When all units are reviewed, user is redirected to "Tasks" page and clicks  "Download" button for the reviewed Task
    - We pull Task data from `GET /tasks/<task_id>/<n_units>/export-results.json` endpoint
