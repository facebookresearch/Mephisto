<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

TODO: [form-builder-app] Complete this reamde with details about each command

## Commands

- [mephisto config](#mephisto-config)
- [mephisto check](#mephisto-check)
- [mephisto requesters](#mephisto-requesters)
- [mephisto register](#mephisto-register)
- [mephisto wut](#mephisto-wut)
- [mephisto scripts](#mephisto-scripts)
- [mephisto metrics](#mephisto-metrics)
- [mephisto review_app](#mephisto-reviewapp)
- [mephisto form_composer](#mephisto-formcomposer)


### mephisto config

Set up a data directory where the results of your crowdsourcing tasks will be stored.
For more details you can consult [Setup section in quickstart.md](docs/web/docs/guides/quickstart.md#setup).


### mephisto check

Check that everything is set up correctly.
For more details you can consult [Setup section in quickstart.md](docs/web/docs/guides/quickstart.md#setup).


### mephisto requesters

Use the command to see registered requesters.
For more details you can consult [Docs for Requesters](docs/web/docs/reference/requesters.md#requesters).


### mephisto register

Use the command to register requesters a new requester.
For more details you can consult [Docs for Requesters](docs/web/docs/reference/requesters.md#requesters) and 
[Setup section in quickstart.md](docs/web/docs/guides/quickstart.md#setup).


### mephisto wut

Dig for more information about specific configuration arguments.
For more details you can consult [First Task Tutorial](docs/web/docs/guides/tutorials/first_task.md#21-discovering-options-with-mephisto-wut).


### mephisto scripts

Run scripts from `mephisto/scripts` directory.


### mephisto metrics

Extension to view task health metrics via dashboard using [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/oss/grafana/).
For more details you can consult [Docs for Metrics](docs/web/docs/guides/how_to_use/efficiency_organization/metrics_dashboarding.md).


### mephisto review_app

Run the Web-application to review completed Mephisto tasks.
The UI is fairly intuitive, and for more details you can consult [README.md for TaskReview app](mephisto/review_app/README.md).


### mephisto form_composer

Application to run simple form-based tasks. 
One thing that you need is to provide configs with fields that you need for your task.
For more details you can consult [Docs for Metrics](docs/web/docs/guides/how_to_use/efficiency_organization/metrics_dashboarding.md).
