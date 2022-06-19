from typing import List
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser

def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    acceptable_responses = set(
        ["a", "accept", "ACCEPT", "Accept", "r", "reject", "REJECT", "Reject"]
    )
    accept_response = set(["a", "accept", "ACCEPT", "Accept"])
    reject_response = set(["r", "reject", "REJECT", "Reject"])
    yes_no_responses = set(["yes", "y", "YES", "Yes", "no", "n", "NO", "No"])
    yes_response = set(["yes", "y", "YES", "Yes"])
    no_response = set(["no", "n", "NO", "No"])

    print("\nTask Names:")
    for task_name in task_names:
        print(task_name)
    print("")
    task_name = input(
        "Enter the name of the task that you want to review the tips of: \n"
    )
    print("")
    print(task_name)
    
    
if __name__ == "__main__":
  main()
