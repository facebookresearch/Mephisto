



# Requesters


The requester is an account for a crowd provider.

Use `mephisto requesters` to see registered requesters, and `mephisto register <requester type>` to register.     
## mock


  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|name|str|MOCK_REQUESTER|Name for the requester in the Mephisto DB.|None|True|
|force_fail|bool|False|Trigger a failed registration|None|False|

## mturk


AWS is required to create a new Requester. Please create an IAM user with programmatic access and AmazonMechanicalTurkFullAccess policy at https://console.aws.amazon.com/iam/ (On the "Set permissions" page, choose "Attach existing policies directly" and then select "AmazonMechanicalTurkFullAccess" policy). After creating the IAM user, you should get an Access Key ID and Secret Access Key.  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|name|str|???|Name for the requester in the Mephisto DB.|None|True|
|access_key_id|str|???|IAM Access Key ID|None|True|
|secret_access_key|str|???|IAM Secret Access Key|None|True|

## mturk sandbox


AWS is required to create a new Requester. Please create an IAM user with programmatic access and AmazonMechanicalTurkFullAccess policy at https://console.aws.amazon.com/iam/ (On the "Set permissions" page, choose "Attach existing policies directly" and then select "AmazonMechanicalTurkFullAccess" policy). After creating the IAM user, you should get an Access Key ID and Secret Access Key.  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|name|str|???|Name for the requester in the Mephisto DB.|None|True|
|access_key_id|str|???|IAM Access Key ID|None|True|
|secret_access_key|str|???|IAM Secret Access Key|None|True|
