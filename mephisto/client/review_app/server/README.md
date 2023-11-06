# TaskReview app API

---

`GET /tasks`

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

`GET /tasks/{id}`

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

`GET /tasks/{id}/worker-units-ids`

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

`GET /qualifications`

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

`POST /qualifications`

Create a new qualification

```
{
    "name": <str>,
}
```

---

`GET /qualifications/{id}/workers?{task_id=}`

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

`POST /qualifications/{id}/workers/{id}/grant`

Grant qualification to a worker

```
{
    "unit_ids": [<int>, ...],
    "value": <int>,
}
```

---

`POST /qualifications/{id}/workers/{id}/revoke`

Revoke qualification from a worker

```
{
    "unit_ids": [<int>, ...],
}
```

---

`GET /units?{task_id=}{unit_ids=}`

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

`GET /units/details?{unit_ids=}`

Get full input for specified workers results (`units_ids` parameter is mandatory)

```
{
    "units": [
        {
            "id": <int>,
            "inputs": <json str>,  // instructions for worker
            "outputs": <json str>,  // response from worker
            "data": {...},  // any other unit data
        },
        ...  // more units
    ]
}
```

---

`POST /units/approve`

Approve worker's result

```
{
    "unit_ids": [<int>, ...],
    "feedback": <str>,  // optional
    "tips": <int>,  // optional
}
```

---

`POST /units/reject`

Reject worker's result

```
{
    "unit_ids": [<int>, ...],
    "feedback": <str>,  // optional
}
```

---

`POST /units/soft-reject`

Soft-reject worker's result

```
{
    "unit_ids": [<int>, ...],
    "feedback": <str>,  // optional
}
```

---

`POST /workers/{id}/block`

Permanently block a worker

```
{
    "unit_id": <int>,
    "feedback": <str>,
}
```

---

`GET /stats?{task_id=}{worker_id=}{since=}{limit=}`

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

### Error response

Exception are returned via API in this format:

```
{
    "error": <str>,
}
```
