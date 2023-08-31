/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


import { Status } from 'consts/http';
import urls from 'urls';


const MOCK_RESPONSES = process.env.REACT_APP__MOCK_RESPONSES;
const MOCK_RESPONSES_DATA = {
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
        "created_at": '2023-08-28T12:00:56',
      }
    ],
  }
}


function makeRequest(
  method: string,
  url: string,
  data: BodyInit | null,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  log_error_message = '',
  abortController?: AbortController,
  setNotFoundErrorsAction?: SetRequestErrorsActionType,
) {
  if (MOCK_RESPONSES === 'true') {
    const mockData = MOCK_RESPONSES_DATA[url]
    if (mockData !== undefined) {
      setDataAction(mockData);
      return
    }
    // Otherwise we make a real request
  }

  if (!abortController) {
    abortController = new AbortController();
  }

  setErrorsAction(null);
  setLoadingAction(true);

  fetch(url, {
    method: method,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    body: data,
    signal: abortController.signal,
  })
    .then((response) => {
      setLoadingAction(false);

      if (response.ok) {
        response
          .json()
          .then((data) => {
            if (data.validation_errors) {
              setErrorsAction(data.validation_errors);
            } else {
              setDataAction(data);
            }
          })
          .catch((error) => {
            if (response.headers.get('Content-Type') === 'application/json') {
              console.log('Failed to JSON.parse response', error, response);
            } else {
              setDataAction(null);
            }
          });
      } else if (response.status === Status.HTTP_400_BAD_REQUEST) {
        response.json().then((data) => {
          setErrorsAction(data);
        });
      } else if (response.status === Status.HTTP_404_NOT_FOUND) {
        response.json().then((data) => {
          if (setNotFoundErrorsAction) {
            setNotFoundErrorsAction(data);
          } else {
            setErrorsAction(data);
          }
        });
      }
    })
    .catch((error) => {
      setErrorsAction({error: 'Server error'});
      console.error(log_error_message, error);
      setLoadingAction(false);
    });
}


export default makeRequest;
