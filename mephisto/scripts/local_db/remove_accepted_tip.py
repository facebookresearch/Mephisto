"""
Script that allows for accepted tips to be removed.
Accepted tips are collected by retrieving all units and then getting the agent of each unit.
The tips for each agent state is filtered to only collect accepted tips.

For each accepted tip you have the option to remove the tip from the agent state.
"""

import enum
from genericpath import exists
from typing import Any, Dict, List
import csv
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.task_run import TaskRun
from mephisto.scripts.local_db.review_tips_for_task import (
    remove_tip_from_metadata,
)
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.tools.scripts import print_out_task_names
from mephisto.utils.rich import console
from rich import print
from rich.prompt import Prompt
from rich.table import Table, Column
from rich import box


class TipsRemovalType(enum.Enum):
    REMOVE = "y"
    KEEP = "n"


def remove_tip_from_tips_file(
    tips: List[Dict[str, Any]],
    i: int,
    task_run: TaskRun,
):
    """Removes the specified tip row from the csv file"""
    tip_id = tips[i]["id"]
    blueprint_task_run_args = task_run.args["blueprint"]
    if "tips_location" in blueprint_task_run_args:
        tips_location = blueprint_task_run_args["tips_location"]
        does_file_exist = exists(tips_location)
        if does_file_exist == False:
            print(
                "\n[red]You do not have a tips.csv file in your task's output directory[/red]"
            )
            quit()

        lines_to_write = []
        # Getting the row in the csv file
        with open(tips_location) as read_tips_file:
            reader = csv.reader(read_tips_file)
            for row in reader:
                if row[0] != tip_id:
                    lines_to_write.append(row)

        # Writing all rows except the row to remove
        with open(tips_location, "w") as write_tips_file:
            writer = csv.writer(write_tips_file)
            writer.writerows(lines_to_write)


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print_out_task_names("Tips Removal", task_names)
    task_name = Prompt.ask(
        "\nEnter the name of the task that you want to review the tips of",
        choices=task_names,
        show_choices=False,
    ).strip()

    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("[red]No units were received[/red]")
        quit()
    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)
            tips = unit_data["tips"]
            if tips is not None:
                accepted_tips = list(filter(lambda tip: tip["accepted"] == True, tips))
                accepted_tips_copy = accepted_tips.copy()

                for i in range(len(accepted_tips)):
                    current_tip_table = Table(
                        "Property",
                        Column("Value"),
                        title="\nTip {current_tip} of {total_number_of_tips} From Agent {agent_id}".format(
                            current_tip=i + 1,
                            total_number_of_tips=len(accepted_tips),
                            agent_id=unit.agent_id,
                        ),
                        box=box.ROUNDED,
                        expand=True,
                        show_lines=True,
                    )
                    current_tip_table.add_row("Tip Id", accepted_tips[i]["id"])
                    current_tip_table.add_row("Tip Header", accepted_tips[i]["header"])
                    current_tip_table.add_row("Tip Text", accepted_tips[i]["text"])
                    console.print(current_tip_table)

                    removal_response = Prompt.ask(
                        "\nDo you want to remove this tip? (Default: n)",
                        choices=[tips_type.value for tips_type in TipsRemovalType],
                        default=TipsRemovalType.KEEP.value,
                        show_default=False,
                    ).strip()
                    print("")

                    if removal_response == TipsRemovalType.REMOVE.value:
                        remove_tip_from_tips_file(
                            accepted_tips_copy, i, unit.get_task_run()
                        )
                        remove_tip_from_metadata(
                            accepted_tips, accepted_tips_copy, i, unit
                        )
                        print("Removed tip\n")
                    elif removal_response == TipsRemovalType.KEEP.value:
                        print("Did not remove tip\n")
    print("There are no more tips to look at\n")


if __name__ == "__main__":
    main()
