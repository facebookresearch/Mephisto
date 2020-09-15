## API specifications

All of the endpoints below are **`GET`** unless specified otherwise.

These specs are to be implemented in `mephisto/client/api.py`.

Key: `💚 - Data Complete / 💛 - Data Mocked / 💜 - Consumed by UI / 🖤 - Not consumed by UI`

#### WIP Endpoints / Backlog

- Endpoints for actions to modify the review state of a Unit
- Endpoint for getting the URL of a task and it's data to show
- Make error reponse format more consistent across all endpoints / types of errors. Some stuff from the wild:
  - https://stripe.com/docs/api/errors
  - https://cloud.google.com/apis/design/errors#http_mapping

---
## 🕵️‍♀️ Requesters

#### `/requesters`
💚💜 *Shows a list of all the requesters that are available on the local system*

Sample response:
```
{
  "requesters": [
    {
      "provider_type": "mturk",
      "registered": false,
      "requester_id": "1",
      "requester_name": "Bob"
    },
    {
      "provider_type": "mturk",
      "registered": true,
      "requester_id": "2",
      "requester_name": "sally"
    }
  ]
}
```

#### `/requester/<type>`

💚💜 *Provides information on what params to provide if you'd like to set up a requester.*

Sample response:
```
[
  {
    "args": {
      "access_key_id": {
        "choices": null,
        "default": null,
        "dest": "access_key_id",
        "help": "IAM Access Key ID",
        "option_string": "--access-key-id",
        "type": "str"
      },
      // ...
    },
    "desc": "\n            MTurkRequester: AWS are required to create a new Requester.\n            Please create an IAM user with programmatic access and\n            AmazonMechanicalTurkFullAccess policy at\n            'https://console.aws.amazon.com/iam/ (On the \"Set permissions\"\n            page, choose \"Attach existing policies directly\" and then select\n            \"AmazonMechanicalTurkFullAccess\" policy). After creating\n            the IAM user, you should get an Access Key ID\n            and Secret Access Key.\n        "
  }
]
```

#### `/<requester_name>/get_balance` - TODO: Change to `/requester/balance/<requester_name>`

💚💜

[Discussion] Instead of `balance` should we make the endpoint a bit more generic, e.g. `info` or `metadata` instead? [Yes] This is because perhaps not every requester may have the concept of having a budget, although most might.

Sample response:
```
# Success:

{ "balance": 3000 }

# Error:

{ message: "Could not find the requester" } # [501]
```

#### **`POST`** `/requester/<type>/register`

💛🖤

Sample response:
```
# Success:

{
  "success": true
}

# Error:

{
  "msg": "No name was specified for the requester.",
  "success": false
}
```

---
## 🚀 Launching

#### `/launch/options`
💛💜

Sample response:
```
{
  "blueprints": [
    { "name": "Test Blueprint", "rank": 1 },
    { "name": "Simple Q+A", "rank": 2 }
  ],
  "architects": ["Local", "Heroku"]
}
```

#### `/blueprints/<blueprint_name>/arguments`
💛💜

Sample response:
```
{ 
  "args": [
    {
      "name": "Task name",
      "defaultValue": "Default Task Name",
      "helpText": "This is what your task will be named."
    }
  ]
}
```


#### `/architects/<architect_name>/arguments`
💛💜

Sample response:
```
{
  "args": [
    {
      "name": "Port number",
      "defaultValue": 8888,
      "helpText": "Your task will be run on this port."
    }
  ]
}
```

#### **`POST`** `/task_runs/launch`
💛🖤

Sample request:
```
{
  "blueprint_name": "Test Blueprint",
  "blueprint_args": [ { ... } ],
  "architect": "Test Architect",
  "architect_args": [ { ... } ],
  "requester": <requester_id>
}
```

Sample response:
```
# Success:

{
  "success": true
}

# Error:

{
  "success": false,
  # TODO: How should the server provide validation feedback?
}
```

---
## 📥 Review

#### `/task_runs/running`
💛🖤

[Discussion] We need to confirm and communicate what exactly we mean by a "running" task. Based on prior discussions, my suspicion is that this categorization is a little difficult. Let's settle on a technical definition.

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
💛🖤

*Shows tasks with atleast 1 unit that is reviewable.*

Sample response:
```
{
  "total_reviewable": 8,
  "task_runs": TaskRun[]
}
```

#### `/task_runs/<task_id>/units`
💛🖤

Sample response:
```
{
  "unit_id": <unit_id>,
  "view_path": "https://google.com",
  "data": {
    "name": "me"
  }
}
```

#### **`POST`** `/task_runs/<task_id>/units/<unit_id>/accept`
💛🖤

[Discussion] Accept params here to allow giving a bonus?

#### **`POST`** `/task_runs/<task_id>/units/<unit_id>/reject`
💛🖤
