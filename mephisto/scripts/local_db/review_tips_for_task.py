from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print("Task Names:")
    for task_name in task_names:
        print(task_name)
    task_name = input(
        "Enter the name of the task that you want to review the tips of: "
    )
    if task_name not in task_names:
        print("That task name is not valid")
        quit()
    units = mephisto_data_browser.get_units_for_task_name(task_name)
    if len(units) == 0:
        print("No units were received")
        quit()
    print("Tips: ")
    for unit in units:
        unit_parsed_data = mephisto_data_browser.get_data_from_unit(unit)["data"]
        tips = unit_parsed_data["metadata"]["tips"]
        for tip in tips:
            print(tip)


if __name__ == "__main__":
    main()
