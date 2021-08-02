# vNext
- The `layerButtons` object now accepts an `intent` property which can be used to color-code buttons.
- The `<VideoPlayer />` accepts a `videoPlayerProps` object that can be used to forward props to the underlying `react-video-player` object.
- The Layers panel is now scrollable.

# v1.1.0
- **ENHANCEMENT** A helpful message is shown when `<AppShell />` is missing a `layers={...}` prop.
- **NEW** Major update to the Debug Panel. Incorporates `react-json-inspector` for the "Inspect State" tab. A search bar also lets you search through the global state quickly.

---

- **FIX** Fix a bug where actions could show up twice in the Actions Panel for `alwaysOn` layers that are also currently selected.
- **ENHANCEMENT** Add a '⬩' marker next to layers in the actions panel that are selected by virtue of active selection, as opposed to the `alwaysOn` prop. Helpful for debugging and intuiting why certain actions are currenlty shown, both for task creators and annotators.
- **NEW** Add a `hideName` boolean prop to `<Layer />` which can be used to prevent that layer from showing up in the Layers Panel. Useful for layers with a visual component, but no annotation-based interactivity. Default: `false`.
- **NEW** New `layerButtons` prop for `<AppShell />` to allow end-users to create toolbar buttons. Format: `{title: string, icon: string.blueprint-icon, action: fn}`
- **FIX** Fix a bug where actions specified for toolbar buttons were not being fired on click.
- **ENHANCEMENT** Add `dataPathBuilderFor(layerId) -> fn(...layerPathArgs)` to helpers. Usage: `const dataPath = dataPathBuilderFor('VideoLayer'); dataPath('playedSeconds');`
- **NEW** Add a `hideActionsIfUnselected` prop to `<Layer />`. Useful for `alwaysOn` or `onWithGroup` layers that should hide their actions from the Actions Panel when unselected.
- **ENHANCEMENT** `<VideoPlayer />` now updates it's data state with a `playing` boolean.

---

- **BREAKING** Rename the `requestQueuePath` helper to `requestsPathFor`.
- **BREAKING** The global state schema for layers has been updated so that it contains three top level properties: `data`, `config`, and `requests`. `requests` has been moved out of `data` into it's own top-level property. Otherwise, `data` is the same as before. All remaining properties that were specified by the layer config are now moved under the `config` property.
    - To update, all accessors that were not part of the data prop must be updated, e.g. `layer.Video.displayName` -> `layer.Video.config.displayName`.
    - Accessors of `requests` also need to be updated. If you were using `requestQueuePath` before, you should be fine, as long as you apply the other breaking change fix above and rename it to `requestsPathFor`.

# v1.0.5
- [See here for initial release notes](https://github.com/facebookresearch/Mephisto/pull/427)
- BBoxFrame layer
- VideoPlayer layer
