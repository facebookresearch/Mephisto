---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 2
---

# Run TaskReview app


## Run with Docker

---

### Single-step launch

This is the simplest way to launch TaskReview app. In repo root run:

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

### Multi-step launch

TaskReview app consists of the server and client parts. If during development you wish to run them in separate steps:

1. In repo root, launch containers: `docker-compose -f docker/docker-compose.dev.yml up`
2. SSH into running container to run server: `docker exec -it mephisto_dc bash`
3. Inside the container run server: `cd /mephisto && mephisto review_app --host 0.0.0.0 --port 8000 --debug --skip-build`
4. SSH into running container to run client: `docker exec -it mephisto_dc bash`
5. Inside the container run client: `cd /mephisto/mephisto/review_app/client/ && REACT_APP__API_URL=http://localhost:8081 PORT=3000 npm start`
6. Open TaskReview app in your browser at (http://localhost:3001)](http://localhost:3001).
