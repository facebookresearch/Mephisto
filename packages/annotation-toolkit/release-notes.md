### v1.1.0
- Show helpful message when `<AppShell />` is missing a layers prop.
- Fix bug where duplicate actions were showing for selected alwaysOn layers.
- Add a '⬩' marker next to layers in the actions menu that are selected by virtue of selection, as opposed to the `alwaysOn` prop. Helpful for debugging and intuiting why certain actions are shown.
- Add a `hideName` boolean prop to prevent layers from showing up in the Layers Panel. Default: `false`.
- Major update to the DebugPanel. Incorporate `react-json-inspector` for the "Inspect State" tab.
- New `layerButtons` prop for `<AppShell />` to allow end-users to crete buttons.
- Fix bug where toolbar button actions were not activated on click.
- Add `buildDataPath(layerId) -> fn(...layerPathArgs)`. Usage: `const dataPath = buildDataPath('VideoLayer'); dataPath('playedSeconds');`
- Add `hideActionsIfUnselected` prop to `<Layer />`. Useful for `alwaysOn` or `onWithGroup` layers that should hide their actions in the actions menu when unselected.


- **BREAKING**: Rename `requestQueuePath` to `requestsPath` in helpers.
- **BREAKING**: The global state schema for layers has been updated so that it contains two top level properties: `data` and `config` as top level properties. `data` is the same as behavior. All remaining properties that were specified by the layer config are now moved under the `config` property. To update, all accessors that were not part of the data prop must be updated, e.g. `layer.Video.displayName` -> `layer.Video.config.displayName`

### v1.0.5
- [See here for initial release notes](https://github.com/facebookresearch/Mephisto/pull/427)
- BBoxFrame layer
- VideoPlayer layer
