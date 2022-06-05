"""
Script that allows for tips to be approved or rejected. 
An approved tip gets written to the local db and removed from
the AgentState metadata. A rejected tip has the same done 
to it, except that it is not written to the db.
"""

from typing import List
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser


def get_index_of_value(lst: List[str], property: str):
    for i in range(len(lst)):
        if lst[i] == property:
            return i


def remove_tip_from_metadata(tips, tips_copy, i, unit):
    tips_id = [tipObj["id"] for tipObj in tips_copy]
    index_to_remove = get_index_of_value(tips_id, tips[i]["id"])
    assigned_agent = unit.get_assigned_agent()

    if assigned_agent is not None:
        tips_copy.pop(index_to_remove)
        assigned_agent.state.update_metadata({"tips": tips_copy})


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print("\nTask Names:")
    for task_name in task_names:
        print(task_name)
    print("")
    task_name = input(
        "Enter the name of the task that you want to review the tips of: "
    )
    print("")
    if task_name not in task_names:
        print("That task name is not valid")
        quit()
    units = mephisto_data_browser.get_units_for_task_name(task_name)
    if len(units) == 0:
        print("No units were received")
        quit()

    for unit in units:

        unit_parsed_data = mephisto_data_browser.get_data_from_unit(unit)["data"]
        metadata = unit_parsed_data["metadata"]
        tips = metadata["tips"]
        if len(tips) > 0:
            print("Unit id: " + unit.db_id)
            tips_copy = tips.copy()
            for i in range(len(tips)):
                print("Current Tip Text: " + tips[i]["text"] + "\n")
                tip_response = input(
                    "Do you want to accept or reject this tip? accept(a)/reject(r): "
                )
                print("")
                if tip_response == "a" or tip_response == "accept":
                    # persists the tip in the db as it is accepted
                    db.new_tip(task_name=task_name, tip_text=tips[i]["text"])
                    remove_tip_from_metadata(tips, tips_copy, i, unit)
                    print("Tip Accepted\n")

                elif tip_response == "r" or tip_response == "reject":
                    remove_tip_from_metadata(tips, tips_copy, i, unit)
                    print("Tip Rejected\n")
                else:
                    print("That response is not valid")
                    quit()
            print("------------------------------------------\n")


if __name__ == "__main__":
    main()
