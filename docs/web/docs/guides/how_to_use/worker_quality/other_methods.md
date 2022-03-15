---
sidebar_position: 5
---

# Other methods for quality control

While not yet implemented in Mephisto's core codebase, there are a few additional methods of quality control that may be successful. This doc lists a few that we've considered for Mephisto thusfar.

## Worker Agreement

A fairly common method for ensuring that data is of high quality is to check for inter-annotator agreement. Putting the same work out for different annotators to complete is currently supported by mephisto using the `mephisto.blueprint.units_per_assignment` argument on static and remote query tasks. This ensures that the specified number of different workers will complete each task.

Once you have multiple completions, you can write your own review script to parse the results for all `Assignment` of your `TaskRun` to see if the `Unit`s within each `Assignment` have similar enough submitted data.

Partial worker agreement may be a more efficient method of determining whether a worker is performing to your expectations, wherein you sample the tasks from a given worker and relaunch for others to complete and validate.

## Review tasks as tasks

An extension of the above, it may be preferable to create tasks to review the data of other submitted workers. You can then use the results to simplify the time taken reviewing over all samples to just reviewing the borderline cases from your metareviewers.

A review project like this almost certainly would require creating a specific allowlist of workers who are qualified to review the work of others, generally some of your higher performing workers on other tasks or during pilots. 

There's certainly a lot of lift to implement this type of workflow, so we're looking to support this type of functionality within Mephisto in our 1.1 release.

## Multi-tier worker qualification

Some have found it effective to keep local ratings on worker quality such that allowlist and blocklist can be created on the fly for specific tasks. You can certainly extend any review script you use to allow categorizing workers, and then may find that your higher-tiered workers are more appropriate for sensitive tasks, or those that require a quality comparison.

## Contributing

While all of the above methods these aren't yet codified, they should all be able to hook into Mephisto primatives in some form or other. We'd be excited to review contributions for any of the above.
