---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 4
---

# Updating documentation

For large functionality changes, please remember to update `mephisto.ai` documentation.

We use Docusaurus package to make Markdown docs available on the web.

## Run locally in development mode

To run Mephisto docs on your local machine for development (with Docker), run these commands:

```shell
docker-compose -f docker/docker-compose.dev.yml up
docker exec -it mephisto_dc bash
cd /mephisto/docs/web/
yarn
yarn install
yarn start-dev:docker
```

You will now be able to access docs in the browser on [http://localhost:3001/](http://localhost:3001/) with live updates after each saving files from docs.

> NOTE: search will not be available in development mode. If you need to use search, stop development server and use production instruction below

## Run locally in production mode

To test search or whether it will work on production, build and run production server.
Sometimes development server do not raise exceptions which production one can.

```shell
docker-compose -f docker/docker-compose.dev.yml up
docker exec -it mephisto_dc bash
cd /mephisto/docs/web/
yarn
yarn install
yarn build
yarn serve-prod:docker
```
