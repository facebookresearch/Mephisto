from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.scripts.local_db.review_tips_for_task import remove_tip_from_metadata
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.utils.rich import console
from rich import print
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.table import Table, Column
from rich import box


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    task_names_text = """# Task Names:"""
    for task_name in task_names:
        task_names_text += "\n* " + task_name

    task_names_markdown = Markdown(task_names_text)
    console.print(task_names_markdown)
    print("")
    task_name = Confirm.get_input(
        console,
        ":writing_hand:  [green]Enter the name of the task that you want to review the tips of[/green]: \n",
        False,
    ).strip()

    print("")
    while task_name not in task_names:
        print("[red]That task name is not valid[/red]\n")
        task_name = Confirm.get_input(
            console,
            ":writing_hand:  [green]Enter the name of the task that you want to review the tips of[/green]: \n",
            False,
        ).strip()
        print("")
    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("No units were received")
        quit()
    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)
            metadata = unit_data["data"]["metadata"]
            tips = metadata["tips"]
            accepted_tips = list(filter(lambda tip: tip["accepted"] == True, tips))
            accepted_tips_copy = accepted_tips.copy()
            acceptable_removal_responses = set(["yes", "y", "no", "n"])
            for i in range(len(accepted_tips)):
                current_tip_table = Table(
                    "Property",
                    Column("Value", style="blue bold"),
                    title="Current Tip",
                    box=box.ROUNDED,
                    expand=True,
                    show_lines=True,
                )
                current_tip_table.add_row("Tip Id", accepted_tips[i]["id"])
                current_tip_table.add_row("Tip Header", accepted_tips[i]["header"])
                current_tip_table.add_row("Tip Text", accepted_tips[i]["text"])
                console.print(current_tip_table)

                removal_response = Confirm.get_input(
                    console,
                    "\n[green]Do you want to remove this tip?[/green] [magenta]yes(y)/no(n)[/magenta]: \n",
                    False,
                ).strip()
                print("")
                while removal_response not in acceptable_removal_responses:
                    print("[red]That response is not valid[/red]\n")
                    removal_response = Confirm.get_input(
                        console,
                        "[green]Do you want to remove this tip?[/green] [magenta]yes(y)/no(n)[/magenta]: \n",
                        False,
                    ).strip()
                    print("")
                if removal_response == "y" or removal_response == "yes":
                    remove_tip_from_metadata(accepted_tips, accepted_tips_copy, i, unit)
                    print("[green]:wastebasket:  Removed tip[/green]\n")
                elif removal_response == "n" or removal_response == "no":
                    print("[green]Did not remove tip[/green]\n")
    print("[green]There are no more tips to look at :sunglasses:[/green]\n")


if __name__ == "__main__":
    main()
