# annotation-toolkit

This package helps users to build out review & annotation tooling for their research tasks.

[**View storybook here.**](https://annotation-toolkit-storybook.vercel.app/)

### Installation

`annotation-toolkit` requires `global-context-store`, `@blueprintjs/core`, and `@blueprintjs/icons` as peer-dependencies.

```bash
npm install --save annotation-toolkit global-context-store @blueprintjs/core @blueprintjs/icons
```

##### To add CSS:

```jsx
import "annotation-toolkit/build/main.css";
import "@blueprintjs/core/lib/css/blueprint.css";
```

To add CSS for `@blueprintjs/icons` you could link to the CDN in your HTML as such:

`<link href="https://unpkg.com/@blueprintjs/icons@^3.4.0/lib/css/blueprint-icons.css" rel="stylesheet" />`

Additional instructions are provided on the [BlueprintJS website](https://blueprintjs.com/docs/#blueprint/getting-started).

### Usage

Basic setup:

```jsx
import Store from "global-context-store";
import { AppShell } from "annotation-toolkit";

// ...
return (
  <div style={{height: "100vh")> // You'll want to enclose the AppShell in an element with a prescribed height
    <Store>
      <AppShell layers={/* ... */} />
    </Store>
  </div>
)
```

The key to how `annotation-toolkit` works is via Layers.

We provide a few defaults out-of-the-box, however it's also very easy to create your own as well. Contributions back always welcome!

Here's how you would use a Layer:

```jsx
import Store from "global-context-store";
import { AppShell, Layer, VideoPlayer } from "annotation-toolkit";

// ...
return (
  <Store>
    <AppShell layers={() => {
      return (
        <Layer
          displayName="Video"
          icon="video" /* uses blueprintjs icons: https://blueprintjs.com/docs/#icons */
          component={({ id }) => (
            <VideoPlayer
              fps={30}
              id={id}
              src={/* videoURL */}
              scale={0.5}
            />
          )}
        />
      )}} />
  </Store>
)
```

A `<Layer />` automatically shows up in the sidebar. A `<Layer />` can also have child layers. In such a case they will appear as nested layers in the side bar.

When a `<Layer />` is selected, it will render in the main Content panel. Layers also take an optional `alwaysOn` property, in which case they are always shown in the Content panel, even if they are not selected.

A full list of the properties of a `<Layer />` are as follows:


### `<Layer />`

- `displayName`: `string` The name that shows up in the left hand Layers panel for the layer.
- `icon`: `string` A `@blueprintjs/icons` name. Shows up on the left hand side. Highly recommended to specify one.
- `secondaryIcon`: `string` A `@blueprintjs/icons` name. Shows up on the right hand side. Optional.
- `component` - `render prop` The component to render in the content pane when this layer is selected.
- `actions` - `() => React.Node` Specify what actions to have show up in the Actions pane using `@blueprintjs/core`'s `<MenuItem />` components.
- `noPointerEvents` - `bool` Whether this layer should accept pointer events. You may want to use this when you have multiple layers that can be active at the same time to avoid them competing with each other for clicks. For example a Bounding Box layer on top of a VideoPlayer layer may want to set this on so that click events can passthrough to the underlying VideoPlayer component.
- `alwaysOn` - `bool` Always show this layer, even if it's not selected.
- `onWithGroup` - `bool` Always show this layer if it, or one of it's sibling, or it's parent is selected.
- `getData({ store })` - `function` If you would like the rendered component of this layer to receive dynamic props, e.g. as the state of the app updates, you can implement this function. It receives as args a `store` object that represents an instance of the `global-context-store`.
- `onSelect({ store })` - `function` Code to execute when this layer is selected. It receives as args a `store` object that represents an instance of the `global-context-store`.
- `hideName` - `bool` Whether or not to hide the name of the layer in the Layers panel. If the layer name is hidden, this also makes the layer unselectable, though if `alwaysOn = true` then the layer can still be functional. Default: `false`

---

There are also several included components that can be used with the `component` render prop of a `<Layer />`.

### `<BBoxFrame />`

- `label` - Default: `""`
- `color` - Default: `"red"`
- `getCoords({ store} )` 
- `displayWhen({ store })` - Default: `() => true`
- `frameHeight`
- `frameWidth`
- `rectStyles`

### `<VideoPlayer />`

- `src`
- `fps`
- `scale`
- `width`
- `height`

Updates it's data state with:
- `duration`
- `detectedSize`: `[width, height]`
- `playedSeconds`
- `playing`: `boolean`

### `<MovableRect />`

- `id` - The layer id where state will be kept track of under a `kf` data prop.
- `defaultBox` - Where to place the box initially
- `getFrame` - A getter, returns the current frameNumber to render the frame at
- `preload` - Optional, expects an array of objects of form `{x, y, width, height, frameNumber}`.
- `document` - Optional, if you want to use a different document, e.g. within an iframe context
- `getLabel` - Optional, a getter, returns string text for a label to add to the bbox

TODO: Add the following additional optional props, all a callback receiving the frame #:
- `onNextKeyframe`
- `onPreviousKeyframe`
- `onFirstKeyframe`
- `onLastKeyframe`
