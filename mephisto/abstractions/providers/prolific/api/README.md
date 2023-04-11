## Prolific Python SDK

-------------------------------------------------------------------------------



### Usage

Set the API key as an environment variable:

```shell
$ export PROLIFIC_API_KEY='API Key'
```

or use credentials file:

```shell
$ cat ~/.prolific/credentials
API Key
```

or mephisto registration will create this file from the previous way:

```shell
$ mephisto register prolific name=prolific api_key="API Key"
```



-------------------------------------------------------------------------------
### Users

To see fields of `User` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.User`

#### Retrieve user account info

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import User

user: User = prolific_api.Users.me()
```



-------------------------------------------------------------------------------
### Workspaces

To see fields of `Workspace` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Workspace`

#### List

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Workspace

workspace_list: List[Workspace] = prolific_api.Workspaces.list()
```

#### Retrieve

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Workspace

workspace: Workspace = prolific_api.Workspaces.retrieve(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Create

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Workspace

workspace: Workspace = prolific_api.Workspaces.create(
    title='Title',
    description='Description',
)
```



-------------------------------------------------------------------------------
### Projects

To see fields of `Project` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Project`

#### List for Workspace

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Project

project_list: List[Project] = prolific_api.Projects.list_for_workspace(
    workspace_id='XXXXXXXXXXXXXXXXXXXXXXXX',
)
```

#### Retrieve for Workspace

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Project

project: Project = prolific_api.Projects.retrieve_for_workspace(
    workspace_id='XXXXXXXXXXXXXXXXXXXXXXXX',
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
)
```

#### Create for Workspace

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Project

project: Project = prolific_api.Projects.create_for_workspace(
    workspace_id='XXXXXXXXXXXXXXXXXXXXXXXX',
    title='Title',
)
```



-------------------------------------------------------------------------------
### Studies

To see fields of `Study` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Study`

#### List

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Study

study_list: List[Study] = prolific_api.Studies.list()
```

#### List for Project

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Study

study_list: List[Study] = prolific_api.Studies.list_for_project(
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
)
```

#### Retrieve

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Study

study: Study = prolific_api.Studies.retrieve(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Create

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Study

study: Study = prolific_api.Studies.create(
    project='YYYYYYYYYYYYYYYYYYYYYYYYY',
    name='Name',
    internal_name='Internal name',
    description='Description',
    external_study_url='https://mephisto.com/temp',
    prolific_id_option=ProlificIDOption.NOT_REQUIRED,
    completion_option=StudyCompletionOption.CODE,
    completion_codes=dict(
        code='ABC123',
        code_type=StudyCodeType.OTHER,
        actions=[dict(
            action=StudyAction.AUTOMATICALLY_APPROVE,
        )],
    ),
    total_available_places=1,
    estimated_completion_time=10,
    reward=100,
    eligibility_requirements=[],
)
```



-------------------------------------------------------------------------------
### Participant Groups

To see fields of `ParticipantGroup` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.ParticipantGroup`

#### List

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import ParticipantGroup

participan_group_list: List[ParticipantGroup] = prolific_api.ParticipantGroups.list()
# Or for Project
participan_group_list: List[ParticipantGroup] = prolific_api.ParticipantGroups.list(
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
)
```

#### Create

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import ParticipantGroup

participan_group: ParticipantGroup = prolific_api.ParticipantGroups.create(
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
    name='Name',
)
```

#### List of Perticipants for Participant Group

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Participant

participant_list: List[Participant] = prolific_api.ParticipantGroups.list_perticipants_for_group(
    id='PPPPPPPPPPPPPPPPPPPPPPPPP',
)
```



-------------------------------------------------------------------------------
### Bonuses

To see fields of `BonusPayments` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.BonusPayments`

#### Set Up Bonus Payments

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import BonusPayments

bonus_payments: BonusPayments = prolific_api.Bonuses.set_up(
    study_id='XXXXXXXXXXXXXXXXXXXXXXXXX',
    csv_bonuses='60ffe5c8371090c7041d43f8,4.25\n60ff44a1d00991f1dfe405d9,4.25',
)
```

#### Pay

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import BonusPayments

bonus_payments: BonusPayments = prolific_api.Bonuses.set_up(...)
prolific_api.Bonuses.pay(id=bonus_payments.id)
```



-------------------------------------------------------------------------------
### Messages

To see fields of `Message` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Message`

#### List

```python
from datetime import datetime, timedelta
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Message

message_list: List[Message] = prolific_api.Messages.list(user_id='XXXXXXXXXXXXXXXXXXXXXXXXX')
# Or
message_list: List[Message] = prolific_api.Messages.list(
    created_after=(datetime.now() - timedelta(days=10)),
)
```

#### List Unread

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Message

message_list: List[Message] = prolific_api.Messages.list_unread()
```

#### Send

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Message

message: Message = prolific_api.Messages.send(
    body='Message body',
    recipient_id='XXXXXXXXXXXXXXXXXXXXXXXXX',
    study_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
)
```



-------------------------------------------------------------------------------
### Submissions

To see fields of `Submission` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Submission`

#### List

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Submission

submission_list: List[Submission] = prolific_api.Submissions.list()
```

#### Retrieve

```python
from mephisto.abstractions.providers.prolific import api as prolific_api
from mephisto.abstractions.providers.prolific.api.data_models import Submission

submission: Submission = prolific_api.Submissions.retrieve(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```



-------------------------------------------------------------------------------
### Exceptions

```python
from mephisto.abstractions.providers.prolific.api import exceptions

"""
 - exceptions.ProlificException - Base Prolific exception
 - exceptions.ProlificAPIKeyError - API Key was not set
 - exceptions.ProlificRequestError - All errors during requests
 - exceptions.ProlificAuthenticationError - Request errors with status code 401
"""
```
