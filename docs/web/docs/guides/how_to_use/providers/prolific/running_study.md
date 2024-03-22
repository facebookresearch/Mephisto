---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# Steps of running a Study

1. Create inactive Study during TaskRun launch, set its `total_available_places = None`.
(Mephisto will create all required units with `created` status.)
2. Update Study with generated `completion_codes` (we need `Study.id` for it).
3. Publish the Study on Prolific.
4. When Mephisto launches a new Unit, increase `total_available_places` in Prolific Study.
5. When a Unit is expired (i.e. completed or returned), Mephisto launches another Unit.
6. When all Units are expired, the Study is considered completed.
7. The results are reviewed by a user. (All currently active EPGs are dynamically changed,
based on workers' updated custom qualifications.)
