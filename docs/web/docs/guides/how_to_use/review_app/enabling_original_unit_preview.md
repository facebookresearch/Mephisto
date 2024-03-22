---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 3
---

# Enable unit preview in TaskReview app

By default, TaskReview app UI always shows a generic results view (i.e. unit content submitted by worker in the format saved by AgentState, such as `data/data/runs/...../agent_data.json` content).

Additionally, you can enable custom display of unit content (e.g. to show task same way as a worker saw it).
To do so, you will need to create a separate "review" version of your app.
Then TaskReview app UI will show "review" version to reviewer inside an iframe, while "regular" version will be shown to worker.

1. Create `review_app` subdirectory within your app, next to the main `app` subdirectory. Its content should include:
    - Main JS file `review.js` for ReviewApp
        - Example: [review.js](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/webapp/src/review.js)
    - ReviewApp `reviewapp.jsx`
        - Example: [reviewapp.jsx](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/webapp/src/reviewapp.jsx)
    - Separate Webpack config `webpack.config.review.js`
        - Example: [webpack.config.review.js](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/webapp/webpack.config.review.js)

2. Specify in your Hydra YAML, under `mephisto.blueprint` section:
```json
task_source_review: ${task_dir}/webapp/build/bundle.review.js
```

3. Add a separate build command for the "review" bundle
```json
"build:review": "webpack --config=webpack.config.review.js --mode development"
```
Example: [package.json](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/webapp/package.json)

4. Build this "review" bundle by running `npm run build:review` from directory with `package.json`.

5. This `reviewapp.jsx` must satisfy 3 requirements, to interface with TaskReview:
    - Render "review" task version only upon receiving messages with Task data:
        - Example: comment #1 in [reviewapp.jsx](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/webapp/src/reviewapp.jsx)
    - Send messages with displayed "review" page height (to resize containing iframe and avoid scrollbars)
        - Example: comment #2 in [reviewapp.jsx](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/webapp/src/reviewapp.jsx)
        `<div ref={appRef}>`
    - Rendered component must always return reference to `appRef`, like so: `<div ref={appRef}>`
        - Example: comment #3 in [reviewapp.jsx](https://github.com/facebookresearch/Mephisto/blob/main/examples/form_composer_demo/webapp/src/reviewapp.jsx)
