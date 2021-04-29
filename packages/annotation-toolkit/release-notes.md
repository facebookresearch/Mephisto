# v1.1.0
- **ENHANCEMENT** Show helpful message when `<AppShell />` is missing a layers prop.
- **FIX** Fix bug where duplicate actions were showing for selected alwaysOn layers.
- **ENHANCEMENT** Add a '⬩' marker next to layers in the actions menu that are selected by virtue of selection, as opposed to the `alwaysOn` prop. Helpful for debugging and intuiting why certain actions are shown, both for task creators and annotators.
- **NEW** Add a `hideName` boolean prop to `<Layer />` to prevent the layer from showing up in the Layers Panel. Useful for layers with a visual component, but no interactivity. Default: `false`.
- **NEW** Major update to the DebugPanel. Incorporate `react-json-inspector` for the "Inspect State" tab.
- **NEW** New `layerButtons` prop for `<AppShell />` to allow end-users to create toolbar buttons. Format: `{title: string, icon: string.blueprint-icon, action: fn}`
- **FIX** Fix bug where toolbar button actions were not activated on click.
- **ENHANCEMENT** Add `buildDataPath(layerId) -> fn(...layerPathArgs)`. Usage: `const dataPath = buildDataPath('VideoLayer'); dataPath('playedSeconds');`
- Add `hideActionsIfUnselected` prop to `<Layer />`. Useful for `alwaysOn` or `onWithGroup` layers that should hide their actions in the actions menu when unselected.

---

- **BREAKING**: Rename the `requestQueuePath` helper to `requestsPath`.
- **BREAKING**: The global state schema for layers has been updated so that it contains two top level properties: `data` and `config` as top level properties. `data` is the same as behavior. All remaining properties that were specified by the layer config are now moved under the `config` property. To update, all accessors that were not part of the data prop must be updated, e.g. `layer.Video.displayName` -> `layer.Video.config.displayName`

# v1.0.5
- [See here for initial release notes](https://github.com/facebookresearch/Mephisto/pull/427)
- BBoxFrame layer
- VideoPlayer layer
