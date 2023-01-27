#!/bin/bash

# Update the version of a given package in the related package.json file
# under "./examples" and "../mephisto/abstractions/blueprints"
# Currently we support the update of the following packages:
# * mephisto-task
# * bootstrap-chat

# Usage:
# You can sync one package at a time like this:
# ./sync_package_version.sh mephisto-task 1.0.13
# ./sync_package_version.sh bootstrap-chat 1.0.7

# You can also sync all packages together like this:
# ./sync_package_version.sh mephisto-task 1.0.13 bootstrap-chat 1.0.7

possible_dirs=`find ../mephisto/abstractions/blueprints ../examples ../packages -type d \( -name node_modules -o -name tmp -o -name runs -o -name _generated \) -prune -false -o -name 'package.json' -exec dirname {} \;`


sync_package_version() {
    package_name=$1
    new_version=$2

    for dir in $possible_dirs
    do
        (cd "$dir" && pwd && sed -i '' "s/\"$package_name\":.*/\"$package_name\": \"$new_version\",/" package.json)
    done

    echo -e "All $package_name in the files above are updated to version $new_version"
    echo
}

while [ -n "$1" ];
do

	case "$1" in

	mephisto-task)
        sync_package_version $1 $2
        shift
        ;;

	bootstrap-chat)
        sync_package_version $1 $2
        shift
        ;;

	react)
        sync_package_version $1 $2
        shift
        ;;

	react-dom)
        sync_package_version $1 $2
        shift
        ;;

	*) echo "Package $1 version sync is not supported yet" ;;

	esac
	shift
done

exit 0
