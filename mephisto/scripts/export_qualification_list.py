#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.worker import Worker
from mephisto.abstractions.providers.mturk.mturk_worker import MTurkWorker

"""
This script can be used to dump out the contents of one's qualifications 
table. This can be useful for bookkeeping, migrations, or sharing qual lists
"""

def dump_qualifications():
    db = LocalMephistoDB()
    do_all = input('Provide comma separated list of specific qualifications to dump, otherwise all will be saved out.\n> ')
    if len(do_all.strip()) == 0:
        target_qualifications = db.find_qualifications()
    else:
        target_qualification_names = do_all.split(',')
        target_qualifications = [
            db.find_qualifications(qualification_name=n)[0] 
            for n in target_qualification_names
        ]
    outfile_name = input("provide an output filename\n> ")

    result = {}
    for qualification in target_qualifications:
        if qualification.qualification_name.endswith('sandbox'):
            continue
        print(f"Qualification: {qualification.qualification_name}")
        description = input("Provide a useful description for what this qualification entails, blank to skip\n> ")
        if len(description.strip()) == 0:
            continue
        qual_dict = {}
        granted_quals = db.check_granted_qualifications(qualification.db_id)
        for granted_qual in granted_quals:
            worker: Worker = Worker.get(db, granted_qual.worker_id)
            if worker.worker_name.endswith('sandbox'):
                continue
            qual_dict[worker.worker_name] = granted_qual.value
        result[qualification.qualification_name] = {
            'description': description,
            'workers': qual_dict,
        }
    with open(outfile_name, 'w+') as outfile:
        json.dump(result, outfile)
    


if __name__ == '__main__':
    dump_qualifications()