---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# MTurk

## Set up MTurk

If you want to  launch your tasks on MTurk, you'll want to create a requester.
Doing this requires an IAM role on AWS with the `MechanicalTurkFullAccess` permission, on an AWS account that is linked to the requester you want to use.
Once you obtain the API credentials for that role, register these with Mephisto, by creating a new requester (make sure to replace `$ACCESS_KEY` and `$SECRET_KEY` below):

```bash
$ mephisto register mturk \
        name=my_mturk_user \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY
AWS credentials successfully saved in ~/.aws/credentials file.

Registered successfully.
```

where `my_mturk_user` can be any name of your choice referring to this particular requester.

## MTurk Sandbox

For an `mturk_sandbox` requester, you should suffix the requester name with *"_sandbox"* (e.g. `my_mturk_user_sandbox`).

Here's how to register an "mturk_sandbox" requester:

```bash
$ mephisto register mturk_sandbox \
        name=my_mturk_user_sandbox \
        access_key_id=$ACCESS_KEY\
        secret_access_key=$SECRET_KEY

Registered successfully.
```
