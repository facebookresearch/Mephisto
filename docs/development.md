# Developement Environment

We use [pre-commit](https://pre-commit.com/) to enforce code styles on the code base (using `black` for Python and `prettier` for Javascript).

To setup your local codebase to auto-lint and avoid lint test failures for your PRs, please set up pre-commit for your local repo as such:

1. `pip install pre-commit`
2. `pre-commit install` to install git hooks
3. `pre-commit run --all-files` (optional - run ad-hoc against all files)
