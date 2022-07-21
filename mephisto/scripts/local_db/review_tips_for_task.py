"""
Script that allows for tips to be approved or rejected.
Tips are collected by retrieving all units and then getting the agent of each unit.
The agent state has the tip data.

Approving a tip sets the accept property of the tip to be True.
This prevents it from appearing again when running this script.
It is stored in the agent state's metadata and in the assets/tips.csv file
in your task's directory.

Rejecting a tip deletes the tip from the tips list in the AgentState's metadata.
It also removed the row in the assets/tips.csv file in your task's directory.
"""
import csv
from genericpath import exists
from pathlib import Path
from typing import Any, List, Dict, Optional
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import Agent
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from rich import print
from rich import box
from rich.prompt import Prompt
from rich.prompt import FloatPrompt
from rich.table import Table
from mephisto.tools.scripts import print_out_task_names
from mephisto.utils.rich import console
import enum


class TipsReviewType(enum.Enum):
    ACCEPTED = "a"
    REJECTED = "r"
    SKIP = "s"


def get_index_of_value(lst: List[str], property: str) -> int:
    for i in range(len(lst)):
        if lst[i] == property:
            return i
    return 0


def add_row_to_tips_file(task_run: TaskRun, item_to_add: Dict[str, Any]):
    """Adds a row the tips csv file"""
    blueprint_task_run_args = task_run.args["blueprint"]
    if "tips_location" in blueprint_task_run_args:
        tips_location = blueprint_task_run_args["tips_location"]
        does_file_exist = exists(tips_location)
        if does_file_exist == False:
            # Creates the file
            create_tips_file = Path(tips_location)
            try:
                create_tips_file.touch(exist_ok=True)
            except FileNotFoundError:
                print(
                    "\n[red]Your task folder must have an assets folder in it.[/red]\n"
                )
                quit()

        with open(tips_location, "r") as inp, open(tips_location, "a+") as tips_file:
            field_names = list(item_to_add.keys())
            writer = csv.DictWriter(tips_file, fieldnames=field_names)
            reader = csv.reader(inp)
            # Add header if the file is newly created or empty
            if does_file_exist == False or len(list(reader)) == 0:
                writer.writeheader()
            writer.writerow(item_to_add)


def remove_tip_from_metadata(
    tips: List[Dict[str, Any]], tips_copy: List[Dict[str, Any]], i: int, unit: Unit
):
    """Removes a tip from metadata"""
    tips_id = [tip_obj["id"] for tip_obj in tips_copy]
    index_to_remove = get_index_of_value(tips_id, tips[i]["id"])
    assigned_agent: Optional[Agent] = unit.get_assigned_agent()

    if assigned_agent is not None:
        tips_copy.pop(index_to_remove)
        assigned_agent.state.update_metadata(
            property_name="tips", property_value=tips_copy
        )
    else:
        print("[red]An assigned agent was not able to be found for this tip[/red]")
        quit()


def accept_tip(tips: List, tips_copy: List, i: int, unit: Unit) -> None:
    """Accepts a tip in metadata"""
    tips_id = [tip_obj["id"] for tip_obj in tips_copy]
    # gets the index of the tip in the tip_copy list
    index_to_update = get_index_of_value(tips_id, tips[i]["id"])
    assigned_agent = unit.get_assigned_agent()

    if assigned_agent is not None:
        tips_copy[index_to_update]["accepted"] = True
        add_row_to_tips_file(unit.get_task_run(), tips_copy[index_to_update])
        assigned_agent.state.update_metadata(
            property_name="tips", property_value=tips_copy
        )


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print_out_task_names("Tips Review", task_names)
    task_name = Prompt.ask(
        "\nEnter the name of the task that you want to review the tips of",
        choices=task_names,
        show_choices=False,
    ).strip()
    print("")
    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("[red]No units were received[/red]")
        quit()
    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)
            tips = unit_data["tips"]

            if tips is not None and len(tips) > 0:
                tips_copy = tips.copy()
                for i in range(len(tips)):
                    if tips[i]["accepted"] == False:
                        current_tip_table = Table(
                            "Property",
                            "Value",
                            title="\nTip {current_tip} of {total_number_of_tips} From Agent {agent_id}".format(
                                current_tip=i + 1,
                                total_number_of_tips=len(tips),
                                agent_id=unit.agent_id,
                            ),
                            box=box.ROUNDED,
                            expand=True,
                            show_lines=True,
                        )
                        current_tip_table.add_row("Tip Id", tips[i]["id"])
                        current_tip_table.add_row("Tip Header", tips[i]["header"])
                        current_tip_table.add_row("Tip Text", tips[i]["text"])
                        console.print(current_tip_table)

                        tip_response = Prompt.ask(
                            "\nDo you want to (a)ccept, (r)eject, or (s)kip this tip? (Default: s)",
                            choices=[tips_type.value for tips_type in TipsReviewType],
                            default=TipsReviewType.SKIP.value,
                            show_default=False,
                        ).strip()

                        print("")
                        if tip_response == TipsReviewType.ACCEPTED.value:
                            # persists the tip in the db as it is accepted
                            accept_tip(tips, tips_copy, i, unit)
                            print("[green]Tip Accepted[/green]")
                            # given the option to pay a bonus to the worker who wrote the tip
                            bonus = FloatPrompt.ask(
                                "\nHow much would you like to bonus the tip submitter? (Default: 0.0)",
                                show_default=False,
                                default=0.0,
                            )
                            if bonus > 0:
                                reason = Prompt.ask(
                                    "\nWhat reason would you like to give the worker for this tip? NOTE: This will be shared with the worker.(Default: Thank you for submitting a tip!)",
                                    default="Thank you for submitting a tip!",
                                    show_default=False,
                                )
                                worker_id = float(unit_data["worker_id"])
                                worker = Worker.get(db, worker_id)
                                if worker is not None:
                                    bonus_successfully_paid = worker.bonus_worker(
                                        bonus, reason, unit
                                    )
                                    if bonus_successfully_paid:
                                        print(
                                            "\n[green]Bonus Successfully Paid![/green]\n"
                                        )
                                    else:
                                        print(
                                            "\n[red]There was an error when paying out your bonus[/red]\n"
                                        )

                        elif tip_response == TipsReviewType.REJECTED.value:
                            remove_tip_from_metadata(tips, tips_copy, i, unit)
                            print("Tip Rejected\n")
                        elif tip_response == TipsReviewType.SKIP.value:
                            print("Tip Skipped\n")

    print("There are no more tips to review\n")


if __name__ == "__main__":
    main()
