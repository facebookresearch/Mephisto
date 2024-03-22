<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

## Run TaskReview app


### Quick Start

For cross-platform compatibility, TaskReview app can be run in dockerized form.

Let's say we already have local database with completed (but not reviewed) tasks, and we need to run this TaskReview app.

---

#### Launch with Docker

Run `docker-compose` from repo root:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --rm mephisto_dc \
    mephisto review_app --host 0.0.0.0 --port 8000 --debug --force-rebuild --skip-build
```

where

- `--build` - builds image before starting container
- `--publish 8081:8000` - maps docker ports, with `8000` being same port as in `-p` option
- `--rm` - automatically removes the previous container if it already exits
- `mephisto_dc` - container name in `docker-compose.dev.yml` file
- `mephisto review_app --host 0.0.0.0 --port 8000 --debug` - launches Mephisto's TaskReview app service inside the container

Command `mephisto review_app` supports the following options:

- `-h/--host` - host where TaskReview app will be served
- `-p/--port` - port where TaskReview app will be served
- `-d/--debug` - run in debug mode (with extra logging)
- `-f/--force-rebuild` - force rebuild React bundle (use if your Task client code has been updated)
- `-s/--skip-build` - skip all installation and building steps for the UI, and directly launch the server (use if no code has been changed)

Now you can access TaskReview app in your browser at [http://localhost:8081](http://localhost:8081).

---

You can find complete details about TaskReview app on our [docs website](https://mephisto.ai/docs/guides/tutorials/review_app/).
