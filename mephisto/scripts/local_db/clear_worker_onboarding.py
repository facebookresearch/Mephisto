from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
)
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.worker import Worker
from rich import print
from rich.prompt import Prompt, IntPrompt


def main():
    db = LocalMephistoDB()
    worker_id = str(IntPrompt.ask("What is the worker's id:", default=1))
    desired_worker = Worker.get(db, worker_id)

    qualification_name = Prompt.ask(
        "What is the qualification name:", default="test-react-static-qualification"
    )

    OnboardingRequired.clear_onboarding(
        worker=desired_worker, qualification_name=qualification_name
    )
    print("\n[green]Cleared that onboarding qualification[/green]\n")


if __name__ == "__main__":
    main()
