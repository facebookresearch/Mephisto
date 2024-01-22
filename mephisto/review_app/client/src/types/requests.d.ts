/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

type ErrorResponseType = {
  error: string;
};

type SetRequestDataActionType = (data) => void;

type SetRequestErrorsActionType = (errors: ErrorResponseType) => void;

type SetRequestLoadingActionType = (loading: boolean) => void;
