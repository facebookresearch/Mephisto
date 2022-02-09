#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit

db = None


def format_for_printing_data(data):
    global db
    # Custom tasks can define methods for how to display their data in a relevant way
    worker_name = Worker.get(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = contents["times"]["task_end"] - contents["times"]["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    outputs = contents["outputs"]
    output_string = ""
    if outputs["response1"] != '':
        output_string += outputs["response1"] + "\n"
    else:
        output_string += "Original: " + outputs["sentence1"] + "\n"
    output_string += outputs["response2"] + "\n"
    output_string += outputs["response3"] + "\n"
    output_string += outputs["response4"] + "\n"
    if outputs["response5"] != '':
        output_string += outputs["response5"]
    else:
        output_string += "Original: " + outputs["sentence1"]
    return f"-------------------\n{metadata_string}{output_string}"


def main():
    global db
    db = LocalMephistoDB()

    run_examine_or_review(db, format_for_printing_data)


if __name__ == "__main__":
    main()
