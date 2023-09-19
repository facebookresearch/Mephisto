#!/bin/bash

# Until dependabot seems to be running, this script will automatically update any
# dependencies that appear to be vulnerabilities across our javascript packages

if [ $# == 0 ]; then
  DRY_RUN=0
else
  if [ "$1" = "dry-run" ]; then
    DRY_RUN=1
  else
    echo "The only allowed argument to this script is dry-run"
    exit 1
  fi
fi

POSSIBLE_DIRS=`find .. -type d \( -name node_modules -o -name tmp -o -name runs -o -name _generated \) -prune -false -o -name 'package.json' -exec dirname {} \;`

for d in $POSSIBLE_DIRS
do
  if [ $DRY_RUN = 1 ]; then
    (cd "$d" && echo "Checking directory $d" && npm audit)
  else
    (cd "$d" && echo ">> Updating packages for directory $d" && npm i --package-lock-only && npm audit fix)
  fi
done

# If the user has updated things, we'll want to add them to the commit only if we're modifying
# something that already existed. Everything else should be removed

if [ $DRY_RUN = 1 ]; then
  exit 0
else
  git ls-files .. --others --exclude-standard | grep -E "\yarn.lock$" | xargs rm
  git ls-files .. --others --exclude-standard | grep -E "\package-lock.json$" | xargs rm
fi
