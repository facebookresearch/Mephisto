export const frameToMs = (frame, fps) => (frame * 1000) / fps;

export const msToFrame = (ms, fps) => Math.round((ms * fps) / 1000);

export const requestsPath = (layerId) => {
  return buildDataPath(layerId)("requests");
};

export const buildDataPath = (layerId) => (...args) => [
  "layers",
  layerId,
  "data",
  ...args,
];
