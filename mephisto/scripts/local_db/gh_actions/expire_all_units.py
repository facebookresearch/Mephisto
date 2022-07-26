from mephisto.abstractions.databases.local_database import LocalMephistoDB

"""
This script should not be used locally.
It is only used in a GitHub action as it does not automatically expire units.
"""


def main():
    task_name = "react-static-task-with-tips"
    db = LocalMephistoDB()
    tasks = db.find_tasks(task_name=task_name)
    assert len(tasks) >= 1, f"No task found under name {task_name}"
    task_runs = db.find_task_runs(task_id=tasks[0].db_id)
    for task_run in task_runs:
        assignments = task_run.get_assignments()
        for assignment in assignments:
            found_units = assignment.get_units()
            for unit in found_units:
                unit.set_db_status("expired")


if __name__ == "__main__":
    main()
