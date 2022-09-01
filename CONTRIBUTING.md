# Contributing to Mephisto
We want to make contributing to this project as easy and transparent as
possible.

## Pull Requests
We actively welcome your pull requests.

### Core contributions

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
    * This can be done by running `pip install pre-commit; pre-commit install`. This will check the if your code is formatted correctly on each commit.
    * Make sure that pre-commit is installed by following the steps in [this website](https://pre-commit.com/).
6. If you haven't already, complete the Contributor License Agreement ("CLA").

## Cypress Testing
For cypress testing the base url is: http://localhost:3000/?worker_id=x&assignment_id=1

### Running end to end tests on a task:
1. Run the task by running python run_task.py in the appropriate task folder
2. In a separate terminal window go into the webapp directory and run `npm run test`
3. This should open a cypress app
4. It is advised to test in Chrome(Chrome, Electron, and Firefox are all the options) as this browser works well with Cypress.
5. After clicking one of the spec files, the tests from that spec will automatically run

### Troubleshooting:
### There may be a case where there is a baseUrl mismatch.

For example:
Suppose you ran the toxicity detection task and then closed it. This would use assignmentId=1 and assignmentId=2. 

If you then ran the mnist task, for example, then assignmentId=3 and assignmentId=4 would be used. While this task is running you can choose to run cypress tests in a different terminal window by going into the webapp folder and running `npm run test`.

These tests will fail because the base url of http://localhost:3000/?worker_id=x&assignment_id=1 is not associated with the mnist task, it is associated with the toxicity detection task. The correct react-elements will not show up.

There is a way to fix this:
* You can change the base url(found in the cypress.config.js file in the webapp folder) to the current url that you are on. 
    * Make sure to reset the baseUrl back to default("/") if contributing to the repo as the GitHub action will fail otherwise.

## Local Package Development
If you are modifying either the `mephisto-task` or `mephisto-worker-addons` packages you probably want to see your changes propagate to the task that you are working on.

The easiest way to do this is to run a task by doing:
```bash
python run_task.py mephisto.task.post_install_script=link_mephisto_task.sh mephisto.task.force_rebuild=true
```

Setting `mephisto.task.force_rebuild=true` runs `npm build` before running your task. By default the task is only rebuilt if a file is changed in the webapp, not if a linked package is changed.

Setting `mephisto.task.post_install_script=link_mephisto_task.sh` runs the `link_mephisto_task.sh` script after `npm install` is ran and before the task is started. This script should be located in the webapp folder of the task. While this script can do many things, for local package development the primary purpose of it is to link to a local package.

Alternatively, these values can be set in the task's hydra_configs/conf yaml file if you want to forgo typing the above and just type
```bash
python run_task.py
```
instead.

## Task Contributions
Generally we encourage people to provide their own blueprints as part of the repo in which they release their code, though if someone creates a strong case for an abstract `Blueprint` that is generally applicable we'd be happy to review it.

## Contributor License Agreement ("CLA")
In order to accept your pull request, we need you to submit a CLA. You only need
to do this once to work on any of Facebook's open source projects.

Complete your CLA here: <https://code.facebook.com/cla>

## Issues
We use GitHub issues to track public bugs. Please ensure your description is
clear and has sufficient instructions to be able to reproduce the issue.

Facebook has a [bounty program](https://www.facebook.com/whitehat/) for the safe
disclosure of security bugs. In those cases, please go through the process
outlined on that page and do not file a public issue.

## License
By contributing to Mephisto, you agree that your contributions will be licensed
under the LICENSE file in the root directory of this source tree.

## Dependencies
To add a python dependency you need to add the dependency as well as its version number to the pyproject.toml file.
