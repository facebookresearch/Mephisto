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
