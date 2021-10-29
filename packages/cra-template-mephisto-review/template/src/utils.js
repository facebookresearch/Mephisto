import config from "./config";

function getHostname() {
  return config.port
    ? `${window.location.protocol}//${window.location.hostname}:${config.port}`
    : window.location.host;
}

export { getHostname };
