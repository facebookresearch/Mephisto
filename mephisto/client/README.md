## API specifications

All of the endpoints below are **`GET`** unless specified otherwise.


#### WIP Endpoints / Backlog

- Endpoints for actions to modify the review state of a Unit
- Endpoint for getting the URL of a task and it's data to show

---
## Requesters

#### `/requesters`

#### `/requester/<type>`

#### `/<requester_name>/get_balance` - TODO: Change to `/requester/balance/<requester_name>`

Sample response:
```

```

#### **`POST`** `/requester/<type>/register`

---
## Launching

#### `/launch/options`

Sample response:
```
{
    "blueprints": [{"name": "Test Blueprint", "rank": 1}, {"name": "Simple Q+A", "rank": 2}],
    "architects": ["Local", "Heroku"]
}
```

#### `/blueprints/<blueprint_name>/arguments`

#### `/architects/<architect_name>/arguments`

#### **`POST`** `/task_runs/launch`

---
## Review

#### `/task_runs/running`

Sample response:
```
{
  live_task_count: 1,
  task_count: 1,
  task_runs: TaskRun[]
}

# For full example payload, see `task_runs__running` in mephisto/webapp/src/mocks.ts
```

#### `/task_runs/reviewable`

#### `/task_runs/<task_id>/units`

Sample response:
```
{
    "id": <unit_id>,
    "view_path": "https://google.com",
    "data": {
        "name": "me"
    }
}
```

#### **`POST`** `/task_runs/<task_id>/units/<unit_id>/accept`

#### **`POST`** `/task_runs/<task_id>/units/<unit_id>/reject`