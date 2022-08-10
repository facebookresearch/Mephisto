from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
)
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.worker import Worker
from rich import print
from rich.prompt import Prompt

"""
In this script we are asking for a worker_id, but we are actually using it as a worker_name.
In the database a worker_id is a number like 1 or 2, while a worker_name is like "x_sandbox".
However, when looking at an url like: http://localhost:3000/?worker_id=x&assignment_id=45
the worker_id is "x".

As the user is more likely to think of the worker_id as "x" instead of 1, we
are calling the worker_name, the worker_id.

In the url example above, this script would first check if there are any workers with the name x.
If there is one, then that worker's onboarding qualification will be revoked. If there are
more than one worker with that name the script aborts.

If there are no workers with that name, it then tries the name "x_sandbox". The _sandbox
affix is commonly attached to worker names in the backend, so that is why "x_sandbox"
is also tried.
"""


def main():
    db = LocalMephistoDB()
    worker_id = str(Prompt.ask("What is the worker's id:", default="x"))

    desired_worker = db.find_workers(worker_name=worker_id)

    if len(desired_worker) == 0:
        worker_id_with_sandbox = worker_id + "_sandbox"
        sandbox_workers = db.find_workers(worker_name=worker_id_with_sandbox)

        if len(sandbox_workers) == 0:
            print("\n[red]There are no workers with that name[/red]\n")
            quit()

        elif len(sandbox_workers) > 1:
            print("\n[red] There is more that one worker with that name[/red]\n")
            quit()

        clear_onboarding(sandbox_workers[0])
        quit()

    elif len(desired_worker > 1):
        print("\n[red]There is more than one worker with that name[/red]\n")
        quit()

    clear_onboarding(desired_worker[0])


def clear_onboarding(desired_worker: Worker):
    qualification_name = Prompt.ask(
        "What is the qualification name:", default="test-react-static-qualification"
    )

    OnboardingRequired.clear_onboarding(
        worker=desired_worker, qualification_name=qualification_name
    )
    print("\n[green]Cleared that onboarding qualification[/green]\n")


if __name__ == "__main__":
    main()
