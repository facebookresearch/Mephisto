# Mephisto Remote Query Template

This task is an _extremely rough_ bare-bones example of being able to set up a task where the frontend directly connects to the backend using the `useMephistoRemoteProcedureTask` hook from the `mephisto-task` package. It should serve as a decent example of how to get a `RemoteProcedureBlueprint` task up off the ground.

Deploying the task as-is brings up a page where the user needs to click the "query backend" button enough times for the task to be considered ready to submit.

It makes use of the function_registry to use a `"handle_with_model"` method that, admittedly, doesn't use any models, but hopefully demonstrates where a model can fit into this type of task.

As it stands, these queries are still just a single request to single response model, but that should be sufficient for most tasks that want to have a backend in-the-loop for an otherwise frontend-heavy task.