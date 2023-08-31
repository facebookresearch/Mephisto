/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


const API_URL = 'http://localhost:5001';


const urls = {
  client: {
    home: '/',
    qualifications: '/qualifications',
    task: (id) => `/tasks/${id}`,
    tasks: '/tasks',
  },
  server: {
    qualifications: API_URL + '/qualifications/',
    tasks: API_URL + '/tasks/',
  },
};


export default urls;
