from mephisto.abstractions.databases.local_database import LocalMephistoDB
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
        "Enter the name of the task that you want to look at the tips of: "
    )
    print("")
    if task_name not in task_names:
        print("That task name is not valid")
        quit()
    accepted_tips = db.get_tip_by_task_name(task_name)
    for tip in accepted_tips:
      print("Tip Id: " + tip.db_id)
      print("Tip Text: " + tip.tip_text)
      removal_response = input("\nDo you want to remove this tip? yes(y)/no(n): ")
      if removal_response == "y" or removal_response == "yes":
          db.remove_tip(tip.db_id)
          print("Removed tip\n")
      elif removal_response == "n" or removal_response == "no":
          print("Did not remove tip\n")
    


if __name__ == "__main__":
    main()
