from typing import Set
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.scripts.local_db.review_tips_for_task import remove_tip_from_metadata
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print("\nTask Names:")
    for task_name in task_names:
        print(task_name)
    print("")
    task_name = input(
        "Enter the name of the task that you want to look at the tips of: \n"
    )
    print("")
    while task_name not in task_names:
        print("That task name is not valid\n")
        task_name = input(
            "Enter the name of the task that you want to look at the tips of: \n"
        )
        print("")
    units = mephisto_data_browser.get_units_for_task_name(task_name)
    if len(units) == 0:
        print("No units were received")
        quit()
    for unit in units:
        unit_data = mephisto_data_browser.get_data_from_unit(unit)
        metadata = unit_data["data"]["metadata"]
        tips = metadata["tips"]
        accepted_tips = list(filter(lambda tip: tip["accepted"] == True), tips)
        accepted_tips_copy = accepted_tips.copy()
        acceptable_removal_responses = set(["yes", "y", "no", "n"])
        for i in range(len(accepted_tips)):
            print("Tip Id: " + accepted_tips[i]["id"])
            print("Tip Header: " + accepted_tips[i]["header"])
            print("Tip Text: " + accepted_tips[i]["text"])
            removal_response = input(
                "\nDo you want to remove this tip? yes(y)/no(n): \n"
            )
            print("")
            while removal_response not in acceptable_removal_responses:
                print("That response is not valid\n")
                removal_response = input(
                    "\nDo you want to remove this tip? yes(y)/no(n): \n"
                )
                print("")
            if removal_response == "y" or removal_response == "yes":
                remove_tip_from_metadata(accepted_tips, accepted_tips_copy, i, unit)
                print("Removed tip\n")
            elif removal_response == "n" or removal_response == "no":
                print("Did not remove tip\n")


if __name__ == "__main__":
    main()
