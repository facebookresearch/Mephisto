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

from typing import Any, Dict, List
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.unit import Unit
from mephisto.scripts.local_db.review_tips_for_task import get_index_of_value, is_number
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser

yes_no_responses = set(["yes", "y", "YES", "Yes", "no", "n", "NO", "No"])
yes_response = set(["yes", "y", "YES", "Yes"])
no_response = set(["no", "n", "NO", "No"])


def set_feedback_as_reviewed(feedback: List, id: str, unit: Unit) -> None:
    """Sets the reviewed property of a feedback to true"""
    assigned_agent = unit.get_assigned_agent()
    feedback_ids = [feedback_obj["id"] for feedback_obj in feedback]
    index_to_modify = get_index_of_value(feedback_ids, id)
    if assigned_agent is not None:
        feedback[index_to_modify]["reviewed"] = True
        assigned_agent.state.update_metadata(
            property_name="feedback", property_value=feedback
        )


def print_out_feedback_elements(
    filtered_feedback_list: List[Dict[str, Any]],
    is_unreviewed: bool,
    unit: Unit,
    feedback: List[Dict[str, Any]],
) -> None:
    """Prints out the desired feedback object properties from a filtered list"""

    for feedback_obj in filtered_feedback_list:
        print("Feedback Id: " + feedback_obj["id"])
        print("Feedback Question: " + feedback_obj["question"])
        print("Feedback Text: " + feedback_obj["text"])
        print("Feedback Toxicity: " + str(feedback_obj["toxicity"]))
        print("")

        """
        The option to mark feedback as reviewed should be
        presented when viewing unreviewed feedback.
        """

        if is_unreviewed == True:
            mark_feedback_as_reviewed = input(
                "\nDo you want to mark this feedback as reviewed? yes(y)/no(n): "
            )
            while mark_feedback_as_reviewed not in yes_no_responses:
                print("That response is not valid\n")
                mark_feedback_as_reviewed = input(
                    "\nDo you want to mark this feedback as reviewed? yes(y)/no(n): "
                )
            if mark_feedback_as_reviewed in yes_response:
                set_feedback_as_reviewed(feedback, feedback_obj["id"], unit)
                print("\nMarked the feedback as reviewed!")
            elif mark_feedback_as_reviewed in no_response:
                print("\nDid not mark the feedback as reviewed!")
            print("\n")


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print("\nTask Names:")
    for task_name in task_names:
        print(task_name)

    # Getting the task name
    task_name = input(
        "\nEnter the name of the task that you want to review the feedback of: \n"
    )
    print("")
    while task_name not in task_names:
        print("That task name is not valid\n")
        task_name = input(
            "Enter the name of the task that you want to review the feedback of: \n"
        )
        print("")

    # Checking if there are units associated with the task name
    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("No units were received")
        quit()

    # Getting all questions
    questions = set({})
    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)
            feedback = unit_data["feedback"]
            if feedback is not None:
                for current_feedback in feedback:
                    questions.add(current_feedback["question"])
    questions_list = list(questions)
    questions_list.sort()

    # Displaying all the questions alphabetically from the feedback component on the task webapp
    print("Your Questions: ")
    for i in range(len(questions_list)):
        print(str(i) + ": " + questions_list[i])

    # Making sure that the filter index is valid
    filter_by_question_index = input(
        '\nIf you want to filter by a question, enter the number of the question.\nIf you want to see feedback to all questions, enter "-1": '
    )
    while is_number(filter_by_question_index) == False:
        print("\nThe response is invalid as it is not a number")
        filter_by_question_index = input(
            '\nIf you want to filter by a question, enter the number of the question.\nIf you want to see feedback to all questions, enter "-1": '
        )
    filter_by_question_index = int(filter_by_question_index)
    while (
        filter_by_question_index >= len(questions_list) or filter_by_question_index < -1
    ):
        print("\nThat index is not valid(it is either too large or too small)")
        filter_by_question_index = input(
            '\nIf you want to filter by a question, enter the number of the question.\nIf you want to see feedback to all questions, enter "-1": '
        )

    if filter_by_question_index != -1:
        print(
            '\nYou chose to look at feedback from the following question: "'
            + questions_list[filter_by_question_index]
            + '"\n'
        )

    # Allowing user to filter out toxic comments
    filter_toxic_comments = input(
        "Do you want to filter out toxic comments? yes(y)/no(n): "
    )
    while filter_toxic_comments not in yes_no_responses:
        print("That response is not valid\n")
        filter_toxic_comments = input(
            "Do you want to filter out toxic comments? yes(y)/no(n): "
        )

    # Allowing user to see reviewed feedback or unreviewed feedback
    see_unreviewed_feedback = input(
        "Do you want to see unreviewed feedback? yes(y)/no(n): "
    )
    print("")
    while see_unreviewed_feedback not in yes_no_responses:
        print("That response is not valid\n")
        see_unreviewed_feedback = input(
            "Do you want to see unreviewed feedback? yes(y)/no(n): "
        )

    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)
            feedback = unit_data["feedback"]
            if feedback is not None:
                filtered_feedback = feedback.copy()
                if len(feedback) > 0:
                    # Firstly, filter by question if an index is specified
                    if filter_by_question_index != -1:
                        filtered_feedback = list(
                            filter(
                                lambda feedback_obj: feedback_obj["question"]
                                == questions_list[filter_by_question_index],
                                feedback,
                            )
                        )
                    if filter_toxic_comments in yes_response:
                        # Secondly, filter the question feedback for toxicity
                        filtered_feedback = list(
                            filter(
                                lambda feedback_obj: feedback_obj["toxicity"] is None
                                or float(feedback_obj["toxicity"]) < 0.5,
                                filtered_feedback,
                            )
                        )

                    if see_unreviewed_feedback in no_response:
                        # Filter the toxicity feedback to get unreviewed feedback
                        reviewed_feedback = list(
                            filter(
                                lambda feedback_obj: feedback_obj["reviewed"] == True,
                                filtered_feedback,
                            )
                        )
                        print_out_feedback_elements(
                            filtered_feedback_list=reviewed_feedback,
                            is_unreviewed=False,
                            unit=unit,
                            feedback=feedback,
                        )
                    elif see_unreviewed_feedback in yes_response:
                        # Filter the toxicity feedback to get reviewed feedback
                        un_reviewed_feedback = list(
                            filter(
                                lambda feedback_obj: feedback_obj["reviewed"] == False,
                                filtered_feedback,
                            )
                        )
                        print_out_feedback_elements(
                            filtered_feedback_list=un_reviewed_feedback,
                            is_unreviewed=True,
                            unit=unit,
                            feedback=feedback,
                        )

    print(
        "You went through all the {type_of_feedback} feedback {ending}!\n".format(
            type_of_feedback="unreviewed"
            if see_unreviewed_feedback in yes_response
            else "reviewed",
            ending="for this question" if filter_by_question_index != -1 else "",
        )
    )


if __name__ == "__main__":
    main()
