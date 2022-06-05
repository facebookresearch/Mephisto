"""
Script that allows for tips to be approved or rejected. 
An approved tip gets written to the local db and removed from
the AgentState metadata. A rejected tip has the same done 
to it, except that it is not written to the db.
"""

from typing import List
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.worker import Worker
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
        unit_data = mephisto_data_browser.get_data_from_unit(unit)
        metadata = unit_data["data"]["metadata"]
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
                    # given the option to pay a bonus to the worker who wrote the tip
                    is_bonus = input(
                    "Do you want to pay a bonus to this worker for their tip? yes(y)/no(n): "
                    )
                    if is_bonus == "y" or is_bonus == "yes":
                        bonus_amount = input("How much money do you want to give: ")
                        reason = input("What is your reason for the bonus: ")
                        worker_id = float(unit_data["worker_id"])
                        worker =  Worker.get(db, worker_id)
                        if worker is not None:
                            bonus_successfully_paid = worker.bonus_worker(bonus_amount, reason, unit)
                            if bonus_successfully_paid:
                                print("Bonus Successfully Paid!\n")
                            else:
                                print("There was an error when paying out your bonus\n")
                    elif is_bonus != "n" and is_bonus != "no":
                        print("That response is not valid\n")
                        quit()

                elif tip_response == "r" or tip_response == "reject":
                    remove_tip_from_metadata(tips, tips_copy, i, unit)
                    print("Tip Rejected\n\n")
                else:
                    print("That response is not valid\n")
                    quit()
    print("There are no more tips to review\n")


if __name__ == "__main__":
    main()
