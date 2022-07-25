/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import { AxiosPromise, AxiosRequestConfig } from "axios";
import { ResponseValues, RefetchOptions, UseAxiosResult } from "axios-hooks";
const isEmpty = require("lodash.isempty");

type AxiosInfo<T, TError> =
  | [
      ResponseValues<T, TError>,
      (
        config?: AxiosRequestConfig,
        options?: RefetchOptions
      ) => AxiosPromise<TError>
    ]
  | [ResponseValues<T, TError>];

type BaseAsyncProps<T, TError> = {
  axiosInfo: UseAxiosResult<T, TError>;
  refetch: Function;
};

type AsyncProps<T, TError> = {
  info: UseAxiosResult<T, TError>;
  onLoading: React.FC<BaseAsyncProps<T, TError>>;
  onError: React.FC<{ error: any } & BaseAsyncProps<T, TError>>;
  onData: React.FC<{ data: T } & BaseAsyncProps<T, TError>>;
  onEmptyData?: React.FC<{ data: T } & BaseAsyncProps<T, TError>>;
  checkIfEmptyFn?: (data: T) => any;
};

export type AsyncComponent<T = any, TError = any> = React.FC<
  AsyncProps<T, TError>
>;

export function createAsync<T, TError>() {
  return Async as AsyncComponent<T, TError>;
}

const Async: AsyncComponent = ({
  info,
  onLoading,
  onError,
  onData,
  onEmptyData,
  checkIfEmptyFn: checkIfEmptyFn,
}) => {
  const [{ data, loading, error }, refetch = () => {}] = info;

  const baseProps: BaseAsyncProps<any, any> = { refetch, axiosInfo: info };

  if (loading) return onLoading({ ...baseProps });
  else if (error) return onError({ error: error.response?.data, ...baseProps });

  const dataToCheckIfEmpty =
    checkIfEmptyFn !== undefined ? checkIfEmptyFn(data) : data;
  const dataIsEmpty = isEmpty(dataToCheckIfEmpty);

  if (dataIsEmpty && onEmptyData !== undefined)
    return onEmptyData({ data, ...baseProps });
  else return onData({ data, ...baseProps });
};

export default Async;

export function mockRequest<T>(
  mockData: T,
  error: any = undefined,
  loading: boolean = false
) {
  const request = {
    data: mockData,
    loading,
    error: error && { response: { data: error } },
  } as ResponseValues<T, T>;
  return [request, () => {}] as [ResponseValues<T, T>, any];
}
