"""
Script that allows for accepted tips to be removed.
Accepted tips are collected by retrieving all units and then getting the agent of each unit.
The tips for each agent state is filtered to only collect accepted tips.

For each accepted tip you have the option to remove the tip from the agent state.
"""

try:
    from rich import print
except ImportError:
    print(
        "\nYou need to have rich installed to use this script. For example: pip install rich\n"
    )
    exit(1)

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.scripts.local_db.review_tips_for_task import remove_tip_from_metadata
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.utils.rich import console
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.table import Table, Column
from rich import box


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    task_names_text = """# Tips Removal\n ## Task Names:"""
    for task_name in task_names:
        task_names_text += "\n* " + task_name

    task_names_markdown = Markdown(task_names_text)
    console.print(task_names_markdown)
    print("")
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
            accepted_tips = list(filter(lambda tip: tip["accepted"] == True, tips))
            accepted_tips_copy = accepted_tips.copy()

            for i in range(len(accepted_tips)):
                current_tip_table = Table(
                    "Property",
                    Column("Value"),
                    title="Tip {current_tip} of {total_number_of_tips}".format(
                        current_tip=i + 1, total_number_of_tips=len(accepted_tips)
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
                    "\nDo you want to remove this tip", choices=["y", "n"]
                ).strip()
                print("")

                if removal_response == "y":
                    remove_tip_from_metadata(accepted_tips, accepted_tips_copy, i, unit)
                    print("Removed tip\n")
                elif removal_response == "n":
                    print("Did not remove tip\n")
    print("There are no more tips to look at\n")


if __name__ == "__main__":
    main()
