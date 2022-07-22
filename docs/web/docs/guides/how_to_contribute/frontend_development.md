---
sidebar_position: 2
---

# Frontend: dev setup

We use [pre-commit](https://pre-commit.com/) to enforce code styles on the code base (using `black` for Python and `prettier` for Javascript).

To setup your local codebase to auto-lint and avoid lint test failures for your PRs, please set up pre-commit for your local repo as such:

1. `pip install pre-commit`
2. `pre-commit install` to install git hooks
3. `pre-commit run --all-files` (optional - run ad-hoc against all files)


## Cypress Testing

This repo uses cypress to conduct frontend end to end tests. Tasks in the examples folder have cypress tests.

To run the tests for a task:
* Launch the task using `python run_task.py`.
* Open cypress by running `npm run test` in the tasks' webapp folder.
* Choose the Chrome browser to run the tests (it is the most consistent).
* Click one of the specs to run its tests.

## Package Development (new)
*For commits after the `yarn-pkg-reorg` tag and for newer packages (`@annotated/*`)*

This repo uses yarn workspaces to manage its front-end dependencies.

**First ensure that you're on the latest version of yarn.**

```bash
$ npm i -g yarn
```

> *Note: Our repo uses yarn v3.0.2 (yarn versions >= 2.0 have codename berry). This version of yarn is checked into the repo at `.yarn/releases` and is targeted by the `"yarnPath"` property in the root `.yarnrc.yml` file. More details can be found [here](https://yarnpkg.com/cli/set/version) and [here](https://yarnpkg.com/configuration/yarnrc#yarnPath).*

**Install all dependencies.**

You can think of this as both running `npm install` in all local workspaces and running `npm link` to link local package dependencies where appropriate.

```bash
$ yarn install

# This is similar to running `lerna --hoist` in the past
```

> You'll notice that individual packages don't have `node_modules/` folders anymore. This is because all packages are hoisted to the top level and placed within the `.yarn/cache` folder. This speeds up `npm install`s, attempts to share dependencies between projects when necessary, and avoids ambiguous module resolutions.

**Build the workspaces**

We can use yarn to build all the dependencies in our project easily.

```bash
$ yarn build-all
```

*Note: You can see the root `package.json` to see the underlying command under this convenience script.*

### Tips & Recipes

- View all of the workspaces in the project:

    ```bash
    $ yarn workspaces list

    ➤ YN0000: .
    ➤ YN0000: docs/sb
    ➤ YN0000: packages/annotated/bbox
    ➤ YN0000: packages/annotated/dev-scripts
    ➤ YN0000: packages/annotated/keypoint
    ➤ YN0000: packages/annotated/shell
    ➤ YN0000: packages/annotated/video-player
    ``` 

- Run a command in a specific workspace

    ```bash
    $ yarn workspace sb build-storybook

    $ yarn workspace @annotated/bbox build
    ```

- Run a command in all workspaces

    ```bash
    $ yarn workspaces foreach -ptA run build
    ```

    More information on the flags for `foreach` can be found [here](https://yarnpkg.com/cli/workspaces/foreach).


## Package Development (old)

*For commits before the `yarn-pkg-reorg` tag or for non-workspace packages, e.g. `global-context-store`, `annotation-toolkit`, `bootstrap-chat`.*


This repo has a few npm packages. If you're developing on them, you may want them to reference each other so your local edits across packages are reflected in your build.
To accomplish this we use [Lerna](https://github.com/lerna/lerna). Lerna is also used to hoist `react` across packages to avoid this dreaded warning/error: https://reactjs.org/warnings/invalid-hook-call-warning.html

```
# In the root of the repo, install Lerna:
npm install

npm run bootstrap
# under the hood, this runs: lerna bootstrap --hoist="{react,react-dom}" which will link all packages that depend on each other, to each other, while also
# hoisting react and react-dom to ensure that all packages uses the same version of react.

# You can then link the common react version hoisted at the root, to your client project located somewhere else on disk.
# Again, from the root:
npm link /other-project/located-somewhere-else/node_modules/react
# This ensure that all projects use the same version of React.

# then in your client project, you can do something like this:
npm link annotation-toolkit global-context-store

# NOTE: It's important to specify the 2 links together! otherwise i'm noticing behavior where
# the second link wipes out the first (npm v7.6.0 & node v15.8.0)
```