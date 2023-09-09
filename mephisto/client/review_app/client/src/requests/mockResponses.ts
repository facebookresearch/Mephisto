/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import urls from 'urls';


export const MOCK_RESPONSES_DATA = {
  [urls.server.tasks]: {
    "tasks": [
      {
        "id": 1,
        "name": 'task1',
        "is_reviewed": false,
        "unit_count": 3,
        "created_at": '2023-08-28T12:00:56',
      },
      {
        "id": 2,
        "name": 'task2',
        "is_reviewed": true,
        "unit_count": 10,
        "created_at": "2023-08-28T12:00:56",
      },
    ],
  },

  [urls.server.qualifications]: {
    "qualifications": [
      {
        "id": 1,
        "name": 'Great workers!',
      },
      {
        "id": 2,
        "name": 'Rejected workers',
      },
      {
        "id": 3,
        "name": 'Some other qualification',
      },
    ],
  },

  [`${urls.server.units}?task_id=1&unit_ids=1%2C2`]: {
    "units": [
      {
        "id": 1,
        "worker_id": 1,
        "task_id": 1,
        "pay_amount": 10,
        "status": "completed",
        "creation_date": "2023-08-28T12:00:56",
        "results": {
          "start": 1693239305.1141467,
          "end": 1693239999.1141467,
          "input_preview": null,
          "output_preview": null,
        },
        "review": {
          "tips": 5,
          "feedback": null,
        },
      },
      {
        "id": 2,
        "worker_id": 2,
        "task_id": 1,
        "pay_amount": 11,
        "status": "completed",
        "creation_date": "2023-08-28T12:00:56",
        "results": {
          "start": 1693239305.1141467,
          "end": 1693239999.1141467,
          "input_preview": null,
          "output_preview": null,
        },
        "review": {
          "tips": 6,
          "feedback": null,
        },
      },
    ],
  },

  [`${urls.server.units}?task_id=1&unit_ids=3`]: {
    "units": [
      {
        "id": 3,
        "worker_id": 2,
        "task_id": 1,
        "pay_amount": 10,
        "status": "completed",
        "creation_date": "2023-08-28T12:10:56",
        "results": {
          "start": 1693239305.1141467,
          "end": 1693239999.1141467,
          "input_preview": null,
          "output_preview": null,
        },
        "review": {
          "tips": 5,
          "feedback": null,
        },
      },
    ],
  },

  [`${urls.server.stats}?task_id=1`]: {
    "stats": {
      "total_count": 3,
      "reviewed_count": 1,
      "approved_count": 1,
      "rejected_count": 0,
      "soft_rejected_count": 0,
    },
  },

  [`${urls.server.stats}?worker_id=1`]: {
    "stats": {
      "total_count": 2,
      "reviewed_count": 1,
      "approved_count": 1,
      "rejected_count": 0,
      "soft_rejected_count": 0,
    },
  },

  [urls.server.tasksWorkerUnitsIds(1)]: {
    "worker_units_ids": [
      {
        "worker_id": 1,
        "unit_id": 1,
      },
      {
        "worker_id": 1,
        "unit_id": 2,
      },
      {
        "worker_id": 2,
        "unit_id": 3,
      },
    ],
  },

  [`${urls.server.unitsDetails}?unit_ids=1`]: {
    "units": [
      {
        "id": 1,
        "inputs": {
          "character_description": "I'm a Prolific character loaded from Mephisto!",
          "character_name": "Loaded Character 1",
          "html": "demo_task.html"
        },
        "outputs": {
          "file1": {
            "lastModified": 1682947666272,
            "name": "Blank diagram.pdf",
            "size": 58955,
            "type": "application/pdf"
          },
          "files": [
            "1693239348196-856712066-file1-Blank diagram.pdf"
          ],
          "rating": "passable"
        }
      }
    ]
  },

  [urls.server.unitsApprove]: {},

  [urls.server.unitsSoftReject]: {},

  [urls.server.unitsReject]: {},
};
