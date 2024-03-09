<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

TODO: [form-builder-app] Complete this reamde with details about each command

## Commands

- [Commands](#commands)
  - [mephisto config](#mephisto-config)
  - [mephisto check](#mephisto-check)
  - [mephisto requesters](#mephisto-requesters)
  - [mephisto register](#mephisto-register)
  - [mephisto wut](#mephisto-wut)
  - [mephisto scripts](#mephisto-scripts)
  - [mephisto metrics](#mephisto-metrics)
  - [mephisto review\_app](#mephisto-review_app)
  - [mephisto form\_composer](#mephisto-form_composer)


### mephisto config

Sets up a data directory to store results of your crowdsourcing tasks.
For more details you can consult [Setup section in quickstart.md](docs/web/docs/guides/quickstart.md#setup).


### mephisto check

Check that Mephisto is set up correctly.
For more details you can consult [Setup section in quickstart.md](docs/web/docs/guides/quickstart.md#setup).


### mephisto requesters

Use the command to list registered requesters (Mock, Mturk, Prolific, etc.).
For more details you can consult [Docs for Requesters](docs/web/docs/reference/requesters.md#requesters).


### mephisto register

Register a new requester within your current Mephisto instance (Mock, Mturk, Prolific, etc.).
For more details you can consult [Docs for Requesters](docs/web/docs/reference/requesters.md#requesters) and
[Setup section in quickstart.md](docs/web/docs/guides/quickstart.md#setup).


### mephisto wut

Find more information about specific configuration arguments.
For more details you can consult [First Task Tutorial](docs/web/docs/guides/tutorials/first_task.md#21-discovering-options-with-mephisto-wut).


### mephisto scripts

Run a script from `mephisto/scripts` directory.


### mephisto metrics

Extension to view task health metrics via dashboard using [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/oss/grafana/).
For more details you can consult [Docs for Metrics](docs/web/docs/guides/how_to_use/efficiency_organization/metrics_dashboarding.md).


### mephisto review_app

Run TaskReview app (a web application) to review your task results.
The UI is fairly intuitive; for more details you can consult [README.md for TaskReview app](mephisto/review_app/README.md).


### mephisto form_composer

Compose and launch a simple form-based data collection task, based on your form configuration.
For more details you can consult [Docs for Form Composer generator](mephisto/generators/form_composer/README.md).
