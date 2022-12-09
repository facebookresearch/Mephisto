---
sidebar_position: 3
---

# Backend: dev setup

We use [pre-commit](https://pre-commit.com/) to enforce code styles on the code base (using `black` for Python and `prettier` for Javascript).

To setup your local codebase to auto-lint and avoid lint test failures for your PRs, please set up pre-commit for your local repo as such:

1. `pip install pre-commit`
2. `pre-commit install` to install git hooks
3. `pre-commit run --all-files` (optional - run ad-hoc against all files)


## Local development mode

If you've installed Mephisto via `pip install mephisto` in the past, in order to get python to use your local version of the package, navigate to your `Mephisto` folder and run:
```bash
pip install -e .
```
This will ensure that your local changes are used in the running version of Mephisto