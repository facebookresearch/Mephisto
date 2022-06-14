"""
Script that allows for feedback to be reviewed.
Feedback are collected by retrieving all units and then getting the agent of each unit.
The agent state has the feedback data.

When running the script you first have the option of
filtering out potential toxic feedback.
After that you have the ability to view reviewed or unreviewed feedback.

If you select reviewed feedback, then the script will print out all of the reviewed feedback.
If you select unreviewed feedback, then the script will print out each
unreviewed feedback and give you the option to mark the feedback as reviewed.
"""

from typing import List
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.unit import Unit
from mephisto.scripts.local_db.review_tips_for_task import get_index_of_value
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser


def set_feedback_as_reviewed(feedback: List, id: str, unit: Unit) -> None:
    """Sets the reviewed property of a feedback to true"""
    assigned_agent = unit.get_assigned_agent()
    feedback_ids = [feedback_obj["id"] for feedback_obj in feedback]
    index_to_modify = get_index_of_value(feedback_ids, id)
    if assigned_agent is not None:
        feedback[index_to_modify]["reviewed"] = True
        assigned_agent.state.update_metadata({"feedback": feedback})


def main():
    yes_no_responses = set(["yes", "y", "YES", "Yes", "no", "n", "NO", "No"])
    yes_response = set(["yes", "y", "YES", "Yes"])
    no_response = set(["no", "n", "NO", "No"])

    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print("\nTask Names:")
    for task_name in task_names:
        print(task_name)
    print("")
    task_name = input(
        "Enter the name of the task that you want to review the feedback of: \n"
    )
    print("")
    while task_name not in task_names:
        print("That task name is not valid\n")
        task_name = input(
            "Enter the name of the task that you want to review the feedback of: \n"
        )
        print("")

    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("No units were received")
        quit()
    filter_toxic_comments = input(
        "Do you want to filter out toxic comments? yes(y)/no(n): "
    )
    while filter_toxic_comments not in yes_no_responses:
        print("That response is not valid\n")
        filter_toxic_comments = input(
            "Do you want to filter out toxic comments? yes(y)/no(n): "
        )

    see_reviewed_feedback = input(
        "Do you want to see already reviewed feedback? yes(y)/no(n): "
    )
    print("")
    while see_reviewed_feedback not in yes_no_responses:
        print("That response is not valid\n")
        see_reviewed_feedback = input(
            "Do you want to see already reviewed feedback? yes(y)/no(n): "
        )
    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)
            metadata = unit_data["data"]["metadata"]
            feedback = metadata["feedback"]
            if len(feedback) > 0:
                if filter_toxic_comments in yes_response:
                    feedback = list(
                        filter(
                            lambda feedback_obj: float(feedback_obj["toxicity"]) < 0.5,
                            feedback,
                        )
                    )

                if see_reviewed_feedback in yes_response:
                    reviewed_feedback = list(
                        filter(
                            lambda feedback_obj: feedback_obj["reviewed"] == True,
                            feedback,
                        )
                    )
                    for i in range(len(reviewed_feedback)):
                        print("Feedback Id: " + reviewed_feedback[i]["id"])
                        print("Feedback Text: " + reviewed_feedback[i]["text"])
                        print("Feedback Toxicity: " + reviewed_feedback[i]["toxicity"])
                        print("")
                elif see_reviewed_feedback in no_response:
                    un_reviewed_feedback = list(
                        filter(
                            lambda feedback_obj: feedback_obj["reviewed"] == False,
                            feedback,
                        )
                    )
                    for i in range(len(un_reviewed_feedback)):
                        print("Feedback Id: " + un_reviewed_feedback[i]["id"])
                        print("Feedback Text: " + un_reviewed_feedback[i]["text"])
                        print(
                            "Feedback Toxicity: " + un_reviewed_feedback[i]["toxicity"]
                        )
                        mark_feedback_as_reviewed = input(
                            "\nDo you want to mark this feedback as reviewed? yes(y)/no(n): "
                        )
                        while mark_feedback_as_reviewed not in yes_no_responses:
                            print("That response is not valid\n")
                            mark_feedback_as_reviewed = input(
                                "\nDo you want to mark this feedback as reviewed? yes(y)/no(n): "
                            )
                        if mark_feedback_as_reviewed in yes_response:
                            set_feedback_as_reviewed(
                                feedback, un_reviewed_feedback[i]["id"], unit
                            )
                            print("\nMarked the feedback as reviewed!")
                        elif mark_feedback_as_reviewed in no_response:
                            print("\nDid not mark the feedback as reviewed!")
                        print("\n")
    print(
        "There is no more {} feedback!\n".format(
            "reviewed" if see_reviewed_feedback in yes_response else "unreviewed"
        )
    )


if __name__ == "__main__":
    main()
