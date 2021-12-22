// export const frameToMs = (frame, fps) => (frame * 1000) / fps;

// export const msToFrame = (ms, fps) => Math.floor((ms * fps) / 1000);

// Given a layerId, returns the conventional nested state path for the
// requests array for a layer. The requests array is used to
// asynchronously send commands to a layer to perform some action.
export const requestsPathFor = (layerId) => {
  return ["layers", layerId, "requests"];
};

// Given a layerId, returns the conventional nested state path for the
// data scoped to that layer. Accepts further arguments to drill further
// into the nested state tree.
//
// Example:
// const getVideoData = dataPathBuilderFor("Video")
// const getVideoData("currenTime");
// const getVideoData("screenshot", "data", "base64")
//
// The last query above would resolve into something
// like ...screenshot.data.base64 in the state tree
export const dataPathBuilderFor = (layerId) => (...args) => [
  "layers",
  layerId,
  "data",
  ...args,
];
