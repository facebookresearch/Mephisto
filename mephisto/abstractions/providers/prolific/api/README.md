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
from mephisto.abstractions.providers.prolific.api.data_models import User
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
user: User = client.Users.me()
```



-------------------------------------------------------------------------------
### Workspaces

To see fields of `Workspace` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Workspace`

#### List

```python
from mephisto.abstractions.providers.prolific.api.data_models import Workspace
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
workspace_list: List[Workspace] = client.Workspaces.list()
```

#### Retrieve

```python
from mephisto.abstractions.providers.prolific.api.data_models import Workspace
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
workspace: Workspace = client.Workspaces.retrieve(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Create

```python
from mephisto.abstractions.providers.prolific.api.data_models import Workspace
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
workspace: Workspace = client.Workspaces.create(
    title='Title',
    description='Description',
)
```

#### Update

```python
from mephisto.abstractions.providers.prolific.api.data_models import Workspace
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
workspace: Workspace = client.Workspaces.update(
    id='XXXXXXXXXXXXXXXXXXXXXXXX',
    description='Description',
)
```

#### Get balance

```python
from mephisto.abstractions.providers.prolific.api.data_models import WorkspaceBalance
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
workspace: WorkspaceBalance = client.Workspaces.get_balance(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```


-------------------------------------------------------------------------------
### Projects

To see fields of `Project` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Project`

#### List for Workspace

```python
from mephisto.abstractions.providers.prolific.api.data_models import Project
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
project_list: List[Project] = client.Projects.list_for_workspace(
    workspace_id='XXXXXXXXXXXXXXXXXXXXXXXX',
)
```

#### Retrieve for Workspace

```python
from mephisto.abstractions.providers.prolific.api.data_models import Project
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
project: Project = client.Projects.retrieve_for_workspace(
    workspace_id='XXXXXXXXXXXXXXXXXXXXXXXX',
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
)
```

#### Create for Workspace

```python
from mephisto.abstractions.providers.prolific.api.data_models import Project
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
project: Project = client.Projects.create_for_workspace(
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
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study_list: List[Study] = client.Studies.list()
```

#### List for Project

```python
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study_list: List[Study] = client.Studies.list_for_project(
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
)
```

#### Retrieve

```python
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study: Study = client.Studies.retrieve(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Create

```python
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study: Study = client.Studies.create(
    project='YYYYYYYYYYYYYYYYYYYYYYYYY',
    name='Name',
    internal_name='Internal name',
    description='Description',
    external_study_url='https://mephisto.com/temp',
    prolific_id_option=ProlificIDOption.URL_PARAMETERS,
    completion_option=StudyCompletionOption.CODE,
    completion_codes=[dict(
        code='ABC123',
        code_type=StudyCodeType.OTHER,
        actions=[dict(
            action=StudyAction.AUTOMATICALLY_APPROVE,
        )],
    )],
    total_available_places=1,
    estimated_completion_time=10,
    reward=100,
    eligibility_requirements=[],
)
```

#### Update

```python
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study: Study = client.Studies.update(
    id='XXXXXXXXXXXXXXXXXXXXXXXX',
    name='Name',
    internal_name='Internal name',
    description='Description',
)
```

#### Remove

```python
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study = client.Studies.remove(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Publish

```python
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study: Study = client.Studies.publish(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Stop

```python
from mephisto.abstractions.providers.prolific.api.data_models import Study
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study: Study = client.Studies.stop(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Calculate Cost

```python
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
study: Union[int, float] = client.Studies.calculate_cost(reward=100, total_available_places=2)
```



-------------------------------------------------------------------------------
### Participant Groups

To see fields of `ParticipantGroup` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.ParticipantGroup`

#### List

```python
from mephisto.abstractions.providers.prolific.api.data_models import ParticipantGroup
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
participan_group_list: List[ParticipantGroup] = client.ParticipantGroups.list()
# Or for Project
participan_group_list: List[ParticipantGroup] = client.ParticipantGroups.list(
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
)
```

#### Retrieve

```python
from mephisto.abstractions.providers.prolific.api.data_models import ParticipantGroup
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
participan_group: ParticipantGroup = client.ParticipantGroups.retrieve(
    id='PPPPPPPPPPPPPPPPPPPPPPPPP',
)
```

#### Create

```python
from mephisto.abstractions.providers.prolific.api.data_models import ParticipantGroup
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
participan_group: ParticipantGroup = client.ParticipantGroups.create(
    project_id='YYYYYYYYYYYYYYYYYYYYYYYYY',
    name='Name',
)
```

#### Remove

```python
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
client.ParticipantGroups.remove(id='PPPPPPPPPPPPPPPPPPPPPPPPP')
```

#### List of Perticipants for Participant Group

```python
from mephisto.abstractions.providers.prolific.api.data_models import Participant
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
participant_list: List[Participant] = client.ParticipantGroups.list_perticipants_for_group(
    id='PPPPPPPPPPPPPPPPPPPPPPPPP',
)
```

#### Add Perticipants to Participant Group

```python
from mephisto.abstractions.providers.prolific.api.data_models import Participant
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
participant_list: List[Participant] = client.ParticipantGroups.add_perticipants_to_group(
    id='PPPPPPPPPPPPPPPPPPPPPPPPP',
    participant_ids=['pppppppppppppppppppppppp1', 'pppppppppppppppppppppppp2'],
)
```

#### Remove Perticipants from Participant Group

```python
from mephisto.abstractions.providers.prolific.api.data_models import Participant
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
participant_list: List[Participant] = client.ParticipantGroups.remove_perticipants_from_group(
    id='PPPPPPPPPPPPPPPPPPPPPPPPP',
    participant_ids=['pppppppppppppppppppppppp1', 'pppppppppppppppppppppppp2'],
)
```



-------------------------------------------------------------------------------
### Bonuses

To see fields of `BonusPayments` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.BonusPayments`

#### Set Up Bonus Payments

```python
from mephisto.abstractions.providers.prolific.api.data_models import BonusPayments
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
bonus_payments: BonusPayments = client.Bonuses.set_up(
    study_id='XXXXXXXXXXXXXXXXXXXXXXXXX',
    csv_bonuses='60ffe5c8371090c7041d43f8,4.25\n60ff44a1d00991f1dfe405d9,4.25',
)
```

#### Pay

```python
from mephisto.abstractions.providers.prolific.api.data_models import BonusPayments
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
bonus_payments: BonusPayments = client.Bonuses.set_up(
    study_id='XXXXXXXXXXXXXXXXXXXXXXXXX',
    csv_bonuses='60ffe5c8371090c7041d43f8,4.25\n60ff44a1d00991f1dfe405d9,4.25',
)
client.Bonuses.pay(id=bonus_payments.id)
```



-------------------------------------------------------------------------------
### Messages

To see fields of `Message` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.Message`

#### List

```python
from datetime import datetime, timedelta
from mephisto.abstractions.providers.prolific.api.data_models import Message
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
message_list: List[Message] = client.Messages.list(user_id='XXXXXXXXXXXXXXXXXXXXXXXXX')
# Or
message_list: List[Message] = client.Messages.list(
    created_after=(datetime.now() - timedelta(days=10)),
)
```

#### List Unread

```python
from mephisto.abstractions.providers.prolific.api.data_models import Message
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
message_list: List[Message] = client.Messages.list_unread()
```

#### Send

```python
from mephisto.abstractions.providers.prolific.api.data_models import Message
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
message: Message = client.Messages.send(
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
from mephisto.abstractions.providers.prolific.api.data_models import Submission
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
submission_list: List[Submission] = client.Submissions.list()
# or
submission_list: List[Submission] = client.Submissions.list(
    study_id='XXXXXXXXXXXXXXXXXXXXXXXX',
)
```

#### Retrieve

```python
from mephisto.abstractions.providers.prolific.api.data_models import Submission
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
submission: Submission = client.Submissions.retrieve(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Approve

```python
from mephisto.abstractions.providers.prolific.api.data_models import Submission
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
submission: Submission = client.Submissions.approve(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```

#### Reject

```python
from mephisto.abstractions.providers.prolific.api.data_models import Submission
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
submission: Submission = client.Submissions.reject(id='XXXXXXXXXXXXXXXXXXXXXXXX')
```



-------------------------------------------------------------------------------
### Eligibility Requirements

To see fields of `EligibilityRequirement` object,
look at `mephisto.abstractions.providers.prolific.api.data_models.EligibilityRequirement`

#### List

```python
from mephisto.abstractions.providers.prolific.api.data_models import EligibilityRequirement
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
submission_list: List[EligibilityRequirement] = client.EligibilityRequirements.list()
```

#### Count participants

```python
from mephisto.abstractions.providers.prolific.prolific_utils import get_authenticated_client

client = get_authenticated_client("prolific")
count: int = client.EligibilityRequirements.count_participants()
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
