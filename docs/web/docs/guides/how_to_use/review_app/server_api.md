---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 5
---

# TaskReview app API

If you wish to customize or improve the TaskReview app, it's helpful to know how its UI and server parts interact.

## User flow

Here is a typical user journey through TaskReview app:

- UI gets list of available tasks from `GET /tasks`
- User selects a task
- UI gets list of available qualifications from `GET /qualifications`
- UI pulls all unit-worker id pairs from  `GET /tasks/{id}/worker-units-ids`
	  - *Due to the need to randomly shuffle units grouped by a worker (to mitigate reviewers bias, etc) we're implementing client-side, not server-side, pagination - client gets full list of all ids, creates a page of unit ids, and then pulls data for those specific units.*
- UI initiates units review by worker:
    - Group units by worker
    - Sort workers by number of their units (fewest units go first)
    - Pick them for review one-by-one
- And then for each worker:
    - UI pulls units by ids from `GET /units?unit_ids=[...]`
    - UI sorts units by `creation_date` and pick them for review one-by-one
        - For each reviewed unit:
            - UI pulls unit details from `GET /units/details?unit_ids=[...]`
            - UI pulls current stats from `GET /stats` (for entire task and for worker within the task)
            - UI renders unit's review representation in an iframe
            - User can choose to reject/accept unit, grant/revoke qualification, and block the worker
- When all units are reviewed, UI redirects user to the "Tasks" page
- User clicks "Show" button in "Stats" column to see hystograms if a Task has suitable data format for them
- User clicks "Open" button in "Chars" column to see Grafana dashboard to investigate a Task
- User clicks "Download" button for a reviewed Task
    - UI pulls Task data from `GET /tasks/<task_id>/<n_units>/export-results.json` endpoint


## API endpoints

These are the API specs enabling TaskReview app UI.

---

### `GET /api/tasks`

Get all available tasks (to select one for review)

**Response**:
```json
{
  "tasks": [
    {
      "created_at": <timestamp>,
      "has_stats": <bool>,
      "id": <int>,
      "is_reviewed": <bool>,
      "name": <str>,
      "unit_all_count": <int>,
      "unit_completed_count": <int>,
      "unit_finished_count": <int>
    },
    ...  // more tasks
  ]
}
```

---

### `GET /api/tasks/{id}`

Get metadata for a task

**URL parameters**:
- `id` - id of a task

**Response**:
```json
{
  "id": <int>,
  "name": <str>,
  "type": <str>,
  "created_at": <timestamp>
}
```

---

### `GET /api/tasks/{id}/export-results`

Compose on the server-side a single file with reviewed task results.

**URL parameters**:
- `id` - id of a task

**Response**:
```json
{
  "file_created": <bool>,
}
```

---

### `GET /api/tasks/{id}/{n_units}/export-results.json`

Serve a single composed file with reviewed task results.

**URL parameters**:
- `id` - id of a task
- `n_units` - amount of units. Needed to clear cached file on server and return a new one

**Response**:
Text file with JSON

---

### `GET /api/tasks/{id}/stats-results`

Assemble stats with results for a Task.

**URL parameters**:
- `id` - id of a task

**Response**:
```json
{
  "stats": {
    <str>: {
      <str>: <str> | <int>, 
      ...
    }, 
    ...
  }, 
  "task_id": <str>, 
  "task_name": <str>, 
  "workers_count": <int>
}
```

---

### `GET /api/tasks/{id}/timeline`

Check if Grafana server is available and redirect or return error.

**URL parameters**:
- `id` - id of a task

**Response**:
```json
{
  "dashboard_url": <str> | null,
  "server_is_available": <bool>,
  "task_name": <str>,
}
```

---

### `GET /api/tasks/{id}/worker-opinions`

Returns all Worker Opinions related to a Task.

**URL parameters**:
- `id` - id of a task

**Response**:
```json
{
  "task_name": <str>,
  "worker_opinions": [
    {
      "data": {
        "attachments": [
          {
            "destination": <str>,
            "encoding": <str>,
            "fieldname": <str>,
            "filename": <str>,
            "mimetype": <str>,
            "originalname": <str>,
            "path": <str>,
            "size": <int>
          },
          ... // more attachments
        ],
        "questions": [
          {
            "answer": <str>,
            "id": <str>,
            "question": <str>,
            "reviewed": <bool>,
            "toxicity": <str> | null
          },
          ... // more questions
        ]
      },
      "unit_data_folder": <str>,
      "unit_id": <str>,
      "worker_id": <str>
    },
    ... // more worker opinions
  ]
}
```

---

### `GET /api/tasks/{id}/worker-units-ids`

Get full, unpaginated list of unit IDs within a task (for subsequent client-side grouping by worker_id and `GET /task-units` pagination)

**URL parameters**:
- `id` - id of a task

**Response**:
```json
{
  "worker_units_ids": [
    {
      "worker_id": <int>,
      "unit_id": <int>,
    },
    ...  // more ids
  ]
}
```

---

### `GET /api/qualifications?{worker_id=}`

Get all available qualifications (to select "approve" and "reject" qualifications).

**GET parameters**:
- `worker_id` - id of a worker, whom these qualification were granted to

**Response**:
```json
{
  "qualifications": [
    {
      "creation_date": <str>,
      "description": <str>,
      "id": <int>,
      "name": <str>,
    },
    ...  // more qualifications
  ]
}
```

---

### `POST /api/qualifications`

Create a new qualification.

**Request**:
```json
{
  "description": <str>,
  "name": <str>, // Required
}
```

**Response**:
```json
{
  "creation_date": <str>,
  "description": <str>,
  "id": <int>,
  "name": <str>,
}
```

---

### `GET /api/qualifications/{id}`

Get metadata for a qualificaition.

**URL parameters**:
- `id` - id of a qualification

**Response**:
```json
{
  "creation_date": <str>,
  "description": <str>,
  "id": <int>,
  "name": <str>,
}
```

---

### `PATCH /api/qualifications/{id}`

Update a qualification.

**URL parameters**:
- `id` - id of a qualification

**Request**:
```json
{
  "description": <str>,
  "name": <str>, // Required
}
```

**Response**:
```json
{
  "creation_date": <str>,
  "description": <str>,
  "id": <int>,
  "name": <str>,
}
```

---

### `DELETE /api/qualifications/{id}`

Delete a qualificaition.

**URL parameters**:
- `id` - id of a qualification

**Response**:
```json
{}
```

---

### `GET /api/qualifications/{id}/details`

Get additional data about a qualification.

**URL parameters**:
- `id` - id of a qualification

**Response**:
```json
{
  "granted_qualifications_count": <int>,
}
```

---

### `GET /api/qualifications/{id}/workers?{task_id=}`

Get list of all bearers of a qualification.

**URL parameters**:
- `id` - id of a qualification

**GET parameters**:
- `task_id` - id of a task

**Response**:
```json
{
  "workers": [
    {
      "worker_id": <int>,
      "value": <int>,
      "worker_review_id": <int>,  // latest grant of this qualification
      "granted_at": <int>,   // maps to `worker_review.creation_date` column
    },
    ...  // more qualified workers
  ]
}
```

---

### `POST /api/qualifications/{id}/workers/{worker_id}/grant`

Grant qualification to a worker.

**URL parameters**:
- `id` - id of a qualification
- `worker_id` - id of a worker

**Request**:
```json
{
  "unit_ids": [<int>, ...], // Required
  "value": <int>,
}
```

**Response**:
```json
{}
```

---

### `PATCH /api/qualifications/{id}/workers/{worker_id}/grant`

Update value of existing granted qualification.

**URL parameters**:
- `id` - id of a qualification
- `worker_id` - id of a worker

**Request**:
```json
{
  "explanation": <str>,
  "value": <int>,
}
```

**Response**:
```json
{}
```

---

### `POST /api/qualifications/{id}/workers/{worker_id}/revoke`

Revoke qualification from a worker.

**URL parameters**:
- `id` - id of a qualification
- `worker_id` - id of a worker

**Request**:
```json
{
  "unit_ids": [<int>, ...], // Required
}
```

**Response**:
```json
{}
```

---

### `PATCH /api/qualifications/{id}/workers/{worker_id}/revoke`

Revoke qualification from a worker (see the difference from `POST` in the code)

**URL parameters**:
- `id` - id of a qualification
- `worker_id` - id of a worker

**Response**:
```json
{}
```

---

### `GET /api/granted-qualifications?{qualification_id=}&{sort=}`

Get list of all granted queslifications

**GET parameters**:
- `qualification_id` - id of a qualification that was granted to a workers
- `sort` - field name and order to sort resonse results (e.g. `value_current`, `-value_current`)

**Response**:
```json
{
  "granted_qualifications": [
    {
      "granted_at": <str>,
      "qualification_id": <str>,
      "qualification_name": <str>,
      "units": [
        {
          "creation_date": <str>,
          "task_id": <str>,
          "task_name": <str>, 
          "unit_id": <str>,
          "value": <int>,
        },
        ... // more units
      ],
      "value_current": <int>,
      "worker_id": <str>,
      "worker_name": <str>,
    },
    ... // more granted qualifications
  ],
}
```

---

### `GET /api/units?{task_id=}&{unit_ids=}&{completed=}`

Get workers' results (filtered by task_id and/or unit_ids, etc) - without full details of input/output. 
At least one filtering parameter must be specified.

**GET parameters**:
- `task_id` - id of a task
- `unit_ids` - ids of units
- `completed` - show completed units or all (`true`/`false`)

**Response**:
```json
{
  "units": [
    {
      "creation_date": <int>,
      "id": <int>,
      "is_reviewed": <bool>,
      "pay_amount": <int>,
      "results": {
        "start": ,
        "end": ,
        "inputs_preview": <json str>,  // optional
        "outputs_preview": <json str>,  // optional
      },
      "review": {
        "bonus": <int>,
        "review_note": <str>,
      },
      "status": <str>,
      "task_id": <int>,
      "worker_id": <int>,
    },
    ...  // more units
  ]
}
```

### `GET /api/units/details?{unit_ids=}`

Get full input for specified workers results (`units_ids` parameter is mandatory).

**GET parameters**:
- `unit_ids` - ids of units (Required)

**Response**:
```json
{
  "units": [
    {
      "has_task_source_review": <bool>,
      "id": <int>,
      "inputs": <json object>,  // instructions for worker
      "metadata": <json object>,  // any metadata (e.g. Worker Opinion, Unit Reviews, etc)
      "outputs": <json object>,  // response from worker
      "prepared_inputs": <json object>,  // prepared instructions from worker
      "unit_data_folder": <str>},  // path to data dir in file system
    },
    ...  // more units
  ]
}
```

---

### `POST /api/units/approve`

Approve worker's result.

**Request**:
```json
{
  "unit_ids": [<int>, ...], // Required
  "review_note": <str>,  // optional
  "bonus": <int>,  // optional
  "send_to_worker": <bool>,  // optional
}
```

**Response**:
```json
{}
```

---

### `POST /api/units/reject`

Reject worker's result.

**Request**:
```json
{
  "unit_ids": [<int>, ...], // Required
  "review_note": <str>,  // optional
  "send_to_worker": <bool>,  // optional
}
```

**Response**:
```json
{}
```

---

### `POST /api/units/soft-reject`

Soft-reject worker's result.

**Request**:
```json
{
  "unit_ids": [<int>, ...], // Required
  "review_note": <str>,  // optional
  "send_to_worker": <bool>,  // optional
}
```

**Response**:
```json
{}
```

---

### `POST /api/workers/{id}/block`

Permanently block a worker.

**URL parameters**:
- `id` - id of a worker

**Request**:
```json
{
  "unit_ids": [<int>, ...], // optional
  "review_note": <str>,  // Required
}
```

**Response**:
```json
{}
```

---

### `GET /api/workers/{id}/qualifications`

Get list of all granted qualifications for a worker.

**URL parameters**:
- `id` - id of a worker

**Response**:
```json
{
  "granted_qualifications": [
    {
      "worker_id": <int>,
      "qualification_id": <int>,
      "value": <int>,
      "granted_at": <int>,  // maps to `worker_review.creation_date` column
    }
  ],
  ...  // more granted qualifications
}
```

---

### `GET /api/review-stats?{task_id=}&{worker_id=}&{since=}&{limit=}`

Get stats of (recent) approvals. Either `task_id` or `worker_id` (or both) must be present.

**GET parameters**:
- `task_id` - id of a task (Required)
- `worker_id` - id of a worker (Required)
- `since` - show stats since date or datetime
- `limit` - limit amount or items in results

**Response**:
```json
{
  "stats": {
    "total_count": <int>,  // within the scope of the filters
    "reviewed_count": <int>,
    "approved_count": <int>,
    "rejected_count": <int>,
    "soft_rejected_count": <int>,
  },
}
```

---

### `GET /api/units/{unit_id}/static/{filename}`

Return static file from `data` directory for specific unit.

**URL parameters**:
- `unit_id` - id of a unit
- `filename` - name of a file, that was uploaded by a worker

**Response**: 
File that was uploaded during unit completion by a worker

---

### Error response

Exception are returned by the API in this format:

```json
{
  "error": <str>,
}
```
