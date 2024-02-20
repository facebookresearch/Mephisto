<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# TaskReview app API

---

`GET /api/tasks`

Get all available tasks (to select one for review)

```
{
    "tasks": [
        {
            "id": <int>,
            "name": <str>,
            "is_reviewed": <bool>,
            "unit_count": <int>,
            "created_at": <timestamp>
        },
        ...  // more tasks
    ]
}
```

---

`GET /api/tasks/{id}`

Get metadata for a task

```
{
    "id": <int>,
    "name": <str>,
    "type": <str>,
    "created_at": <timestamp>
}
```

---

`GET /api/tasks/{id}/export-results`

Compose a single file with reviewed task results

---

`GET /api/tasks/{id}/{n_units}/export-results.json`

Serve a single composed file with reviewed task results

---

`GET /api/tasks/{id}/worker-units-ids`

Get full, unpaginated list of unit IDs within a task (for subsequent client-side grouping by worker_id and `GET /task-units` pagination)

```
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

`GET /api/qualifications`

Get all available qualifications (to select "approve" and "reject" qualifications)

```
{
    "qualifications": [
        {
            "id": <int>,
            "name": <str>,
        },
        ...  // more qualifications
    ]
}
```

---

`POST /api/qualifications`

Create a new qualification

```
{
    "name": <str>,
}
```

---

`GET /api/qualifications/{id}/workers?{task_id=}`

Get list of all bearers of a qualification.

```
{
    "workers": [
        {
            "worker_id": <int>,
            "value": <int>,
            "unit_review_id": <int>,  // latest grant of this qualification
            "granted_at": <int>,   // maps to `unit_review.created_at` column
        },
        ...  // more qualified workers
    ]
}
```

---

`POST /api/qualifications/{id}/workers/{id}/grant`

Grant qualification to a worker

```
{
    "unit_ids": [<int>, ...],
    "value": <int>,
}
```

---

`POST /api/qualifications/{id}/workers/{id}/revoke`

Revoke qualification from a worker

```
{
    "unit_ids": [<int>, ...],
}
```

---

`GET /api/units?{task_id=}{unit_ids=}`

Get workers' results (filtered by task_id and/or unit_ids, etc) - without full details of input/output. At least one filtering parameter must be specified

_NOTE: this edpoint is not currently used in TaskReview app_

```
{
	"units": [
		{
			"id": <int>,
			"worker_id": <int>,
			"task_id": <int>,
			"pay_amount": <int>,
			"status": <str>,
			"creation_date": <int>,
			"results": {
				"start": ,
				"end": ,
				"inputs_preview": <json str>,  // optional
				"outputs_preview": <json str>,  // optional
			},
			"review": {
				"tips": <int>,
				"feedback": <str>,
			}
		},
		...  // more units
	]
}
```

`GET /api/units/details?{unit_ids=}`

Get full input for specified workers results (`units_ids` parameter is mandatory)

```
{
    "units": [
        {
            "has_task_source_review": <bool>,
            "id": <int>,
            "inputs": <json object>,  // instructions for worker
            "outputs": <json object>,  // response from worker
            "prepared_inputs": <json object>,  // prepared instructions from worker
            "unit_data_folder": <str>},  // path to data dir in file system
        },
        ...  // more units
    ]
}
```

---

`POST /api/units/approve`

Approve worker's result

```
{
    "unit_ids": [<int>, ...],
    "feedback": <str>,  // optional
    "tips": <int>,  // optional
}
```

---

`POST /api/units/reject`

Reject worker's result

```
{
    "unit_ids": [<int>, ...],
    "feedback": <str>,  // optional
}
```

---

`POST /api/units/soft-reject`

Soft-reject worker's result

```
{
    "unit_ids": [<int>, ...],
    "feedback": <str>,  // optional
}
```

---

`POST /api/workers/{id}/block`

Permanently block a worker

```
{
    "unit_id": <int>,
    "feedback": <str>,
}
```

---

`GET /api/stats?{task_id=}{worker_id=}{since=}{limit=}`

Get stats of (recent) approvals. Either `task_id` or `worker_id` (or both) must be present.

```
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

`GET /api/units/{unit_id}/static/{filename}`

Return static file from `data` directory for specific unit.

Response: file.

---

### Error response

Exception are returned via API in this format:

```
{
    "error": <str>,
}
```
