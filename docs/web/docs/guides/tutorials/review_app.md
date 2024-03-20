---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 5
---

# Reviewing task results

Once you've [installed Mephisto](/docs/guides/quickstart/), you have access to the `mephisto` command line utility,
which can launch task review workflow `$ mephisto review_app ...`.

## Overview

Results can be reviewed for tasks that have some data collected.
Note that results will look nicer if task specifies UI code for TaskReview app (see [Enable unit preview in TaskReview app](/docs/guides/how_to_use/review_app/enabling_original_unit_preview/)).

## Quick Start

For cross-platform compatibility, TaskReview app can be run in dockerized form.

---

### Launch with Docker

Run `docker-compose` from repo root:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --rm mephisto_dc \
    mephisto review_app --host 0.0.0.0 --port 8000 --debug --force-rebuild --skip-build
```

---

For more details:
- [Running TaskReview app](/docs/guides/how_to_use/review_app/running/)
- [Enable unit preview in TaskReview app](/docs/guides/how_to_use/review_app/enabling_original_unit_preview/)
- [TaskReview app UI](/docs/guides/how_to_use/review_app/overview/)
- [Server API](/docs/guides/how_to_use/review_app/server_api/)
