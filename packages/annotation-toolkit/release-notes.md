# v1.1.2-beta
- **NEW** Adds in the `<MovableRect />` component with built-in linear interpolation between keyframes. Usage:
   ```js
   <MovableRect defaultBox={[50, 200, 100, 100]} getFrame={() => {
        return currentFrameNumber;
    }} />
    ```
- **ENHANCEMENT** - VideoPlayer playing can be toggled by clicking on the video.
- **ENHANCEMENT** - Add a getLabel property to MovableRect that adds a label to the box.
- **NEW** - Add `getInterpolatedFrames(allKeyframes)` helper to convert keyframes into interpolated frames, frame-by-frame. Returns array of: `{frame, value: [x, y, width, height]}`
- **NEW** `<VideoPlayer />` will now read and execute callback fns from the data prop `renderSteps`. These steps can be defined by client code. The expected format of `renderSteps` is an object as such:
   ```js
   {
     'render-key-id': (ctx, now, metadata, canvasRef) => {...}
   }
   ```

---

- **BREAKING** - Layer actions now require a render prop instead of React node.

# v1.1.1
- **NEW** Support for generating `<VideoPlayer />` screenshots via the requests queue. Usage:
  ```js
  push(requestsPathFor("Video"), {
    type: "screenshot",
    payload: {
      size: [x, y, cropWidth, cropHeight], // size is of original dimensions before videoScale is applied
      callback: (info) => {
        // info is the base64 encoded image data
      },
    }   
  })
  ```
- **FIX** The `<VideoPlayer />` no longer requires an `id` property. This requirement was introduced as an unintentional constraint in v1.1.0 and wasn't present in v1.0.x. It will automatically detect its `id` via context if none is provided. If one is provided, it will use that instead (however this `id` MUST correspond to an already defined `id` for another layer). In shell-mode, we now print a nice error message when an `id` if no layer is found matching this `id`. In standalone mode, this `id` can be any arbitrarily created `id`.
- **ENHANCEMENT** The `layerButtons` object now accepts an `intent` property which can be used to color-code buttons.
- **ENHANCEMENT** The `<VideoPlayer />` accepts a `videoPlayerProps` object that can be used to forward props to the underlying `react-video-player` object.
- **ENHANCEMENT** The Layers Panel is now scrollable.
- **NEW** `<AppShell />` accepts an `instructionsPane` renderProp to draw out an information panel on the top right hand corner of the screen above the actions pane.
- **FIX** Big performance bump by avoiding unnecessary renders within the LayerPanel.
- **FIX** Fix character encoding of active layer actions indicator.
- **NEW** Add support for `secondaryLabel` which works similar to `secondaryIcon` for `<Layer />` components.
- **NEW** A portal ref component is available via global state at `_unsafe.portalRef` for other BlueprintJS components such as dialogs and modals to use.
- **NEW** `contextHeight` prop for the `<AppShell />` to control the height of the Context Panel. Default: `200px`.

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
