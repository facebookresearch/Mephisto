## Run TaskReview app


#### Run Server application

```shell
mephisto review_app --host 0.0.0.0 --port 5000 --debug True
```

where

- `-h`/`--host` - host address (optional, default: `"127.0.0.1"`)
- `-p`/`--port` - port (optional, default: `5000`)
- `-d`/`--debug` - debug (optional, default: `None`)


#### Run Client application

```shell
cd <REPO_FOLDER>/mephisto/client/review_app/client/
npm start
```

To run on a port other than default, you can specify it like so:

```shell
PORT=3002 npm start
```

## Prepare your Task app

You will need to create a separate "review" version of your app (that will be shown to reviewer inside an iframe), in addition to "task" version (shown to crowd worker).

1. Create `review_app` subdirectory of your app, next to the main `app` subdirectory. Its content should include:
    - Main JS file `review.js` for ReviewApp
        - Example: [review.js](../../../examples/remote_procedure/mnist_for_review/webapp/src/review.js)
    - ReviewApp `reviewapp.jsx`
        - Example: [reviewapp.jsx](../../../examples/remote_procedure/mnist_for_review/webapp/src/reviewapp.jsx)
    - Separate Webpack config `webpack.config.review.js`
        - Example: [webpack.config.review.js](../../../examples/remote_procedure/mnist_for_review/webapp/webpack.config.review.js)

2. Specify in your Hydra YAML, under mephisto.blueprint section:
```json
task_source_review: ${task_dir}/webapp/build/bundle.review.js
```

3. Add a separate build command for the "review" bundle
```json
"build:review": "webpack --config=webpack.config.review.js --mode development"
```
Example: [package.json](../../../examples/remote_procedure/mnist_for_review/webapp/package.json)

4. Build this "review" bundle by running `npm run build:review` from directory with `package.json`.

5. This `reviewapp.jsx` must satisfy 3 requirements, to interface with TaskReview:
    - Render "review" task version only upon receiving messages with Task data:
        - Example: comment #1 in [reviewapp.jsx](../../../examples/remote_procedure/mnist_for_review/webapp/src/reviewapp.jsx)
    - Send messages with displayed "review" page height (to resize containing iframe and avoid scrollbars)
        - Example: comment #2 in [reviewapp.jsx](../../../examples/remote_procedure/mnist_for_review/webapp/src/reviewapp.jsx)
        <div ref={appRef}>
    - Rendered component must always return reference to `appRef`, like so `<div ref={appRef}>`
        - Example: comment #3 in [reviewapp.jsx](../../../examples/remote_procedure/mnist_for_review/webapp/src/reviewapp.jsx)

-----

#### Quick Start with Docker-Compose

For cross-platform compatibility, TaskReview app can be run in dockerized form. _In the following example port values for TaskReview client and server can be customized if needed._

Let's say we already have local database with data for completed (but not reviewed) tasks, and we need to run TaskReview app.

1. In `docker/entrypoints` directory, create new entrypoint `server.my_review.sh` following this template:
   ```shell
   #!/bin/sh
   set -e

   # Build your Task app (MNIST is used as an example)
   cd /mephisto/examples/remote_procedure/mnist_for_review/webapp/
   npm install
   npm run build:review

   # Buid TaskReview app client
   cd /mephisto/mephisto/client/review_app/client/
   npm install

   # Set main directory as repo root directory
   cd /mephisto

   exec "$@"
   ```
2. In `docker` directory, duplicate [docker-compose.dev.yml](../../../docker/docker-compose.dev.yml) file under new name `docker-compose.local.yml`.
    - Change line `- ./entrypoints/server.prolific.sh:/entrypoint.sh` -> `- ./entrypoints/server.my_review.sh:/entrypoint.sh`
3. Go to repo root folder.
4. Launch docker containers `docker-compose -f docker/docker-compose.local.yml up`.
5. Start TaskReview app server `docker-compose -f docker/docker-compose.local.yml exec fb_mephisto mephisto review_app -h 0.0.0.0 -p 8000 -d True`,
6. Start TaskReview app client `docker-compose -f docker/docker-compose.local.yml exec fb_mephisto bash -c 'cd /mephisto/mephisto/client/review_app/client/ && REACT_APP__API_URL=http://localhost:8081 PORT=3000 npm start'`.
7. Open TaskReview app in your browser at (http://localhost:3001)](http://localhost:3001).
8. (Optional) In `docker/envs` directory, duplicate [env.dev](../../../docker/envs/env.dev) file under new name `env.local`.
- In `docker-compose.local.yml`, change line `env_file: envs/env.dev` -> `env_file: envs/env.local`
- Into this new `env.local` file, paste lines `REACT_APP__API_URL=http://localhost:8081` and `PORT=3000`
- Now you don't have to specify these env parameters every time you run TaskReview app client, and the command is shortened to `docker-compose -f docker/docker-compose.local.yml exec fb_mephisto bash -c 'cd /mephisto/mephisto/client/review_app/client/ && npm start'`
