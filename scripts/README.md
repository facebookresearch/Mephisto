# Mephisto repo scripts

This directory contains helper scripts used for the purpose of maintaining the Mephisto repo.

If you're looking for python scripts for using Mephisto, you should check the [mephisto/scripts](`https://github.com/facebookresearch/Mephisto/blob/main/mephisto/scripts`) directory.

## UpdateJSDeps

Recursively goes through all of the directories searching for js packages, and resolves potential security vulnerabilities. `./update_js_deps.sh dry-run` calls this without actually making the changes.
