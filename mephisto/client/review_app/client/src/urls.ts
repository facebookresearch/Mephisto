/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const API_URL = "http://localhost:5001";

const urls = {
  client: {
    home: "/",
    task: (id) => `/tasks/${id}`,
    tasks: "/tasks",
  },
  server: {
    qualifications: API_URL + "/qualifications",
    qualificationWorkers: (id) => API_URL + `/qualifications/${id}/workers`,
    qualificationGrantWorker: (id, workerId) =>
      API_URL + `/qualifications/${id}/workers/${workerId}/grant`,
    qualificationRevokeWorker: (id, workerId) =>
      API_URL + `/qualifications/${id}/workers/${workerId}/revoke`,
    stats: API_URL + "/stats",
    task: (id) => API_URL + `/tasks/${id}`,
    tasks: API_URL + "/tasks",
    tasksWorkerUnitsIds: (id) => API_URL + `/tasks/${id}/worker-units-ids`,
    unitReviewHtml: (id) => API_URL + `/units/${id}/review.html`,
    units: API_URL + "/units",
    unitsApprove: API_URL + "/units/approve",
    unitsDetails: API_URL + "/units/details",
    unitsReject: API_URL + "/units/reject",
    unitsSoftReject: API_URL + "/units/soft-reject",
    workersBlock: (id) => API_URL + `/workers/${id}/block`,
  },
};

export default urls;
