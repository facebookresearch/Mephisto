# Mephisto Remote Query Examples

This directory contains examples of using remote queries. The `template` example consists of the boilerplate with pointers about how the code interacts with the data model (and hints on how to build your own task), while the `mnist` example shows what a functioning model-in-the-loop task would really run like.

While neither of these tasks use it, `RemoteProcedureBlueprint` tasks are also provided with a list of the previous calls made in `initialTaskData.previous_requests` in the case of a reconnect. This can be useful for re-establishing state if a worker refreshes the page.