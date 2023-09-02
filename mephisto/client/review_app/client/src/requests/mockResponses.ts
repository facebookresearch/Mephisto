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

  [`${urls.server.units}?task_id=1`]: {
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

  [`${urls.server.stats}?task_id=1`]: {
    "stats": {
      "total_count": 3,
      "reviewed_count": 3,
      "approved_count": 1,
      "rejected_count": 1,
      "soft_rejected_count": 1,
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
        "worker_id": 1,
        "unit_id": 3,
      },
    ],
  },
};
