# MTurk Scripts
This directory contains scripts that may be useful for Mephisto users that use MTurk as a crowd provider. Descriptions of the scripts and what they do can be found here:

# Cleanup
The cleanup script `cleanup.py` is to be used when a run exits due to a catastrophic failure, such as a power outage, sudden reboot, or series of eager Ctrl-C presses. It will search through any tasks that seem to be active and running, and allow users to select to take them down.

Upon run, the script will ask what requester you want to clean up from. It will try to find all of the HITs currently associated with that requester, and see if any of them appear to be broken or active. (If you have an active job running, there's currently no clear way to distinguish between those and ones from a previously failed run). After this the script will ask for whether you want to clean up by title, or just clean up all of the tasks. 

# Soft-block Workers by MTurk ID
The script `soft_block_workers_by_mturk_id.py` exists to allow a smooth transition into using Mephisto for users that may have blocklists in other locations. Mephisto doesn't directly allow granting Mephisto-backed qualifications to workers that are not in the MephistoDB, but this script can be used to assign such a qualification to MTurk workers just by their ID. 

To use the script, enter the requester name that you would like to assign the block from, the Mephisto qualification name you will be using to block, and then a newline separated list of the MTurk IDs you want to block. After this, entering a blank newline will block all of the given workers.