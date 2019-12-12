import React from "react";
import {
  AxiosError,
  AxiosResponse,
  AxiosPromise,
  AxiosRequestConfig
} from "axios";
const isEmpty = require("lodash.isempty");

// Start below: type definitions copied from the axios-hooks lib which
// unfortunately doesn't export them:
export interface ResponseValues<T> {
  data: T;
  loading: boolean;
  error?: AxiosError;
  response?: AxiosResponse;
}

interface RefetchOptions {
  useCache?: boolean;
}
/* End above: copied type defs from axios-hook */

type AxiosInfo<T> =
  | [
      ResponseValues<T>,
      (config?: AxiosRequestConfig, options?: RefetchOptions) => AxiosPromise<T>
    ]
  | [ResponseValues<T>];

type BaseAsyncProps<T> = {
  axiosInfo: AxiosInfo<T>;
  refetch: Function;
};

type AsyncProps<T> = {
  info: AxiosInfo<T>;
  onLoading: React.FC<BaseAsyncProps<T>>;
  onError: React.FC<{ error: any } & BaseAsyncProps<T>>;
  onData: React.FC<{ data: T } & BaseAsyncProps<T>>;
  onEmptyData?: React.FC<{ data: T } & BaseAsyncProps<T>>;
  checkIfEmptyFn?: (data: T) => any;
};

export type AsyncComponent<T = any> = React.FC<AsyncProps<T>>;

export function createAsync<T>() {
  return Async as AsyncComponent<T>;
}

const Async: AsyncComponent = ({
  info,
  onLoading,
  onError,
  onData,
  onEmptyData,
  checkIfEmptyFn: checkIfEmptyFn
}) => {
  const [{ data, loading, error }, refetch = () => {}] = info;

  const baseProps: BaseAsyncProps<any> = { refetch, axiosInfo: info };

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
    error: error && { response: { data: error } }
  } as ResponseValues<T>;
  return [request, () => {}] as [ResponseValues<T>, any];
}
