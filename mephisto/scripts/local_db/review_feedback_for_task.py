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

import enum
from typing import Any, Dict, List
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import Agent
from mephisto.data_model.unit import Unit
from mephisto.scripts.local_db.review_tips_for_task import get_index_of_value
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from rich import print
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt
from mephisto.tools.scripts import print_out_task_names
from mephisto.utils.rich import console
from rich.table import Table
from rich import box

yes_response = set(["yes", "y", "YES", "Yes"])


class FeedbackReviewType(enum.Enum):
    YES = "y"
    NO = "n"
    REVIEWED = "r"
    UNREVIEWED = "u"


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


def print_out_reviewed_feedback_elements(
    filtered_feedback_list: List[Dict[str, Any]], agent: Agent
) -> None:
    if agent is not None:
        feedback_table = Table(
            "Id",
            "Question",
            "Text",
            "Toxicity",
            title="Reviewed Feedback For Agent: " + agent.get_agent_id(),
            box=box.ROUNDED,
            expand=True,
            show_lines=True,
        )
        filtered_feedback_list.sort(key=lambda x: x["question"])
        for feedback_obj in filtered_feedback_list:
            feedback_table.add_row(
                feedback_obj["id"],
                feedback_obj["question"],
                feedback_obj["text"],
                "[red]" + feedback_obj["toxicity"] + "[/red]"
                if float(feedback_obj["toxicity"]) > 0.5
                else feedback_obj["toxicity"],
            )
        console.print(feedback_table)


def print_out_unreviewed_feedback_elements(
    filtered_feedback_list: List[Dict[str, Any]],
    unit: Unit,
    feedback: List[Dict[str, Any]],
) -> None:
    """Prints out the desired feedback object properties from a filtered list"""
    i = 0
    agent = unit.get_assigned_agent()
    for feedback_obj in filtered_feedback_list:
        feedback_table = Table(
            "Property",
            "Value",
            title="Unreviewed Feedback {current_feedback} of {total_feedback} From Agent {agent_id}".format(
                current_feedback=i + 1,
                total_feedback=len(filtered_feedback_list),
                agent_id=agent.get_agent_id() if agent is not None else "-1",
            ),
            box=box.ROUNDED,
            expand=True,
            show_lines=True,
        )
        feedback_table.add_row("Id", feedback_obj["id"])
        feedback_table.add_row("Question", feedback_obj["question"])
        feedback_table.add_row("Text", feedback_obj["text"])
        feedback_table.add_row("Toxicity", feedback_obj["toxicity"])

        console.print(feedback_table)
        mark_feedback_as_reviewed = Prompt.ask(
            "\nDo you want to mark this feedback as reviewed? (Default: y)",
            choices=[FeedbackReviewType.YES.value, FeedbackReviewType.NO.value],
            default=FeedbackReviewType.YES.value,
            show_default=False,
        )
        if mark_feedback_as_reviewed == FeedbackReviewType.YES.value:
            set_feedback_as_reviewed(feedback, feedback_obj["id"], unit)
            print("\nMarked the feedback as reviewed!")

        elif mark_feedback_as_reviewed == FeedbackReviewType.NO.value:
            print("\nDid not mark the feedback as reviewed!")

        print("")
        i += 1


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    print_out_task_names("Feedback Review", task_names)
    task_name = Prompt.ask(
        "\nEnter the name of the task that you want to review the tips of",
        choices=task_names,
        show_choices=False,
    ).strip()
    print("")

    # Checking if there are units associated with the task name
    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("[red]No units were received[/red]")
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
    questions_text = """## Questions"""
    # Displaying all the questions alphabetically from the feedback component on the task webapp
    for i in range(len(questions_list)):
        questions_text += "\n" + str(i) + ". " + questions_list[i]
    questions_markdown = Markdown(questions_text)
    console.print(questions_markdown)
    # Making sure that the filter index is valid
    filter_by_question_index = IntPrompt.ask(
        '\nIf you want to filter feedback by a question, then enter the question number to filter on.\nIf you want to see feedback to all questions, enter "-1" (Default: -1)',
        choices=[str(i) for i in range(-1, len(questions_list))],
        default=-1,
        show_default=False,
    )

    if filter_by_question_index != -1:
        print(
            "\nYou chose to look at feedback from the following question: [bold]"
            + str(questions_list[filter_by_question_index])
            + "[/bold]\n"
        )

    # Allowing user to filter out toxic comments
    filter_toxic_comments = Prompt.ask(
        "Do you want to filter out toxic comments? (Default: n)",
        choices=[FeedbackReviewType.YES.value, FeedbackReviewType.NO.value],
        default=FeedbackReviewType.NO.value,
        show_default=False,
    )

    # Allowing user to see reviewed feedback or unreviewed feedback
    see_unreviewed_feedback = Prompt.ask(
        "Do you want to see (r)eviewed or (u)nreviewed feedback? (Default: u)",
        choices=[
            FeedbackReviewType.REVIEWED.value,
            FeedbackReviewType.UNREVIEWED.value,
        ],
        default=FeedbackReviewType.UNREVIEWED.value,
        show_default=False,
    )
    print("")

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
                    if filter_toxic_comments == FeedbackReviewType.YES.value:
                        # Secondly, filter the question feedback for toxicity
                        filtered_feedback = list(
                            filter(
                                lambda feedback_obj: feedback_obj["toxicity"] is None
                                or float(feedback_obj["toxicity"]) < 0.5,
                                filtered_feedback,
                            )
                        )

                    if see_unreviewed_feedback == FeedbackReviewType.REVIEWED.value:
                        # Filter the toxicity feedback to get reviewed feedback
                        reviewed_feedback = list(
                            filter(
                                lambda feedback_obj: feedback_obj["reviewed"] == True,
                                filtered_feedback,
                            )
                        )
                        print_out_reviewed_feedback_elements(
                            filtered_feedback_list=reviewed_feedback,
                            agent=unit.get_assigned_agent(),
                        )
                    elif see_unreviewed_feedback == FeedbackReviewType.UNREVIEWED.value:
                        # Filter the toxicity feedback to get unreviewed feedback
                        un_reviewed_feedback = list(
                            filter(
                                lambda feedback_obj: feedback_obj["reviewed"] == False,
                                filtered_feedback,
                            )
                        )
                        print_out_unreviewed_feedback_elements(
                            filtered_feedback_list=un_reviewed_feedback,
                            unit=unit,
                            feedback=feedback,
                        )

    print(
        "[green]You went through all the {type_of_feedback} feedback{ending}![/green]\n".format(
            type_of_feedback="unreviewed"
            if see_unreviewed_feedback == FeedbackReviewType.UNREVIEWED.value
            else "reviewed",
            ending=" for this question" if filter_by_question_index != -1 else "",
        )
    )


if __name__ == "__main__":
    main()
