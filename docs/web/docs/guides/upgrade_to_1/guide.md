---
sidebar_position: 1
---

# Upgrade Guide

1. Update the Mephisto library to v1.
    - If you set up Mephisto using `pip install -e`, ensure you pull the latest version down from the git repo.
    - Or if you set up Mephisto using the pip wheel: `pip install Mephisto -U`
2. Ensure that your front-end code is using the latest packages, by running the following **in your task's webapp folder**.
    ```bash
    npm install --save mephisto-task@2
    npm install --save bootstrap-chat@2 # if applicable
    ```
3. For webapps using `mephisto-task`: Migrate any usage of `sendMessage` in your front-end code to `sendLiveUpdate`.   
4. [Migrate your run scripts](../run_scripts) to use the newly introduced syntax, aimed to reduce boilerplate.


:::info

*Optional*: If you'd like to set up metrics, you can also run the CLI command: `mephisto metrics install`

:::
