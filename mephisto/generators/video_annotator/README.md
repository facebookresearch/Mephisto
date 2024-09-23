<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

This package provides `VideoAnnotator` widget for React-based front-end development for Mephisto tasks.


# How to Run

To create and launch a VideoAnnotator task, first create your JSON form configuration,
and then run the below commands.

Let's assume you're running it with `local` architect and `mock` provider. Once FormComposer launches, in the console you will see URLs like this: `http://localhost:3000/?worker_id=x&assignment_id=1`.

To view your Task as a worker, take one of these links and paste it in your browser.
If launched with `docker-compose`, replace port `3000` with the remapped port (e.g. for `3001:3000` it will be port `3001`).


## With docker-compose

You can launch VideoAnnotator inside a Docker container:

1. Prepare and validate configs as it described it in [Config files](https://mephisto.ai/docs/guides/how_to_use/video_annotator/configuration/setup/) and
[Running application](https://mephisto.ai/docs/guides/how_to_use/video_annotator/running/)

2. Run annotator itself (see details in [Running application](https://mephisto.ai/docs/guides/how_to_use/video_annotator/running/))

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --publish 3001:3000 \
    --rm mephisto_dc \
    mephisto video_annotator
```

---

For more details, see [FormComposer overview](https://mephisto.ai/docs/guides/how_to_use/video_annotator/overview/)
