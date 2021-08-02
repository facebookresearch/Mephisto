# Development Environment

We use [pre-commit](https://pre-commit.com/) to enforce code styles on the code base (using `black` for Python and `prettier` for Javascript).

To setup your local codebase to auto-lint and avoid lint test failures for your PRs, please set up pre-commit for your local repo as such:

1. `pip install pre-commit`
2. `pre-commit install` to install git hooks
3. `pre-commit run --all-files` (optional - run ad-hoc against all files)

# Front-end Development

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