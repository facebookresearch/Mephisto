import { configure } from "axios-hooks";
import Axios, { AxiosRequestConfig } from "axios";

const axios = Axios.create({
  baseURL: "http://localhost:5000/api/v1/"
});

declare module "axios" {
  export interface AxiosRequestConfig {
    delayed?: boolean | number;
  }
}

// type CustomAxiosRequestConfig = AxiosRequestConfig & { delayed?: boolean };

axios.interceptors.request.use(config => {
  if (config.delayed) {
    return new Promise(resolve =>
      setTimeout(
        () => resolve(config),
        config.delayed === true
          ? 600
          : config.delayed === false
          ? 0
          : config.delayed
      )
    );
  }
  return config;
});

configure({ axios });

export default axios;
