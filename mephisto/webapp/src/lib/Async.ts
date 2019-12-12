import React from "react";
import { AxiosError, AxiosResponse, AxiosPromise } from "axios";
const isEmpty = require("lodash.isempty");

// copied from axios-hooks which doesn't export the following type:
export interface ResponseValues<T> {
  data: T;
  loading: boolean;
  error?: AxiosError;
  response?: AxiosResponse;
}

type AsyncProps<T> = {
  info:
    | [ResponseValues<T>, (config?: any, options?: any) => AxiosPromise<T>]
    | [ResponseValues<T>];
  onLoading: React.FC<any>;
  onError: React.FC<any>;
  onData: React.FC<any>;
  onEmptyData?: React.FC<any>;
  checkIfEmptyFn?: Function;
};

const Async: React.FC<AsyncProps<any>> = ({
  info,
  onLoading,
  onError,
  onData,
  onEmptyData,
  checkIfEmptyFn: checkIfEmptyFn
}) => {
  const [{ data, loading, error }, refetch] = info;

  const baseProps = { refetch, axiosInfo: info };

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
  loading = false,
  error = undefined
) {
  const request = {
    data: mockData,
    loading,
    error
  } as ResponseValues<T>;
  return [request, () => {}] as [ResponseValues<T>, any];
}
