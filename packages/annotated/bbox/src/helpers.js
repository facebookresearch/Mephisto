// TODO: should these state helper methods be moved to their own package?
// Right now they are exported from @annotated/shell, however that package
// has dependencies on @blueprintjs/core which is overkill

export const requestsPathFor = (layerId) => {
  return ["layers", layerId, "requests"];
};

export const dataPathBuilderFor = (layerId) => (...args) => [
  "layers",
  layerId,
  "data",
  ...args,
];
