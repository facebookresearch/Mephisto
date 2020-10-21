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

POSSIBLE_DIRS=`find .. -type d \( -name node_modules -o -name tmp -o -name runs -o -name _generated \) -prune -false -o -name 'package-lock.json' -exec dirname {} \;`

for d in $POSSIBLE_DIRS
do
  if [ $DRY_RUN = 1 ]; then
    (cd "$d" && echo "Checking directory $d" && npm audit)
  else
    (cd "$d" && echo "Updating packages for directory $d" && npm audit fix)
  fi
done
