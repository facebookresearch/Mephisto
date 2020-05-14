from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.assignment import Unit

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

DO_REVIEW = True

units = mephisto_data_browser.get_units_for_task_name(input("Input task name: "))

tasks_to_show = input("Tasks to see? (a)ll/(u)nreviewed: ")
if (tasks_to_show in ['all', 'a']):
    DO_REVIEW = False
else:
    units = [u for u in units if u.get_status() == 'completed']

def format_for_printing_data(data):
    # Custom tasks can define methods for how to display their data in a relevant way
    worker_name = Worker(db, data['worker_id']).worker_name
    contents = data['data']
    duration = contents['times']['task_end'] - contents['times']['task_start']
    metadata_string = f"Worker: {worker_name}\nUnit: {data['unit_id']}\nDuration: {int(duration)}\n"

    inputs = contents['inputs']
    inputs_string = (
        f"Character: {inputs['character_name']}\nDescription: {inputs['character_description']}\n"
    )

    outputs = contents['outputs']
    output_string = (
        f"   Rating: {outputs['rating']}\n"
    )
    found_files = outputs.get('files')
    if found_files is not None:
        file_dir = Unit(db, data['unit_id']).get_assigned_agent().get_data_dir()
        output_string += f"   Files: {found_files}\n"
        output_string += f"   File directory {file_dir}\n"
    else:
        output_string += f"   Files: No files attached\n"
    return f"-------------------\n{metadata_string}{inputs_string}{output_string}"

disqualification_name = None
for unit in units:
    print(format_for_printing_data(mephisto_data_browser.get_data_from_unit(unit)))
    if DO_REVIEW:
        keep = input("Do you want to accept this work? (a)ccept, (r)eject, (p)ass")
        if keep == "a":
            unit.get_assigned_agent().approve_work()
        elif keep == "r":
            reason = input("Why are you rejecting this work?")
            unit.get_assigned_agent().reject_work(reason)
        elif keep == "p":
            # General best practice is to accept borderline work and then disqualify
            # the worker from working on more of these tasks
            # Can also mark this task as being something to leave out of your dataset
            # by keeping track of the UnitID somewhere
            # TODO(#93) it would be nice to be able to put that into the database as PASSED
            if disqualification_name == None:
                disqualification_name = input(
                    "Please input the qualification name you are using to soft block for this task: "
                )
            agent = unit.get_assigned_agent()
            agent.approve_work()
            worker = agent.get_worker()
            worker.grant_qualification(disqualification_name, 1)

