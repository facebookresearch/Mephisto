# annotation-toolkit

This package helps users to build out review & annotation tooling for their research tasks.

### Installation

`annotation-toolkit` requires `global-context-store`, `@blueprintjs/core`, and `@blueprintjs/icons` as peer-dependencies.

```bash
npm install --save annotation-toolkit global-context-store @blueprintjs/core @blueprintjs/icons
```

### Usage

Basic setup:

```jsx
import Store from "global-context-store";
import { AppShell } from "annotation-toolkit";

// ...
return (
  <Store>
    <AppShell layers={/* ... */} />
  </Store>
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

- `displayName`: `string` The name that shows up in the left hand Layers panel for the layer.
- `icon`: `string` A `@blueprintjs/icons` name. Shows up on the left hand side. Highly recommended to specify one.
- `secondaryIcon`: `string` A `@blueprintjs/icons` name. Shows up on the right hand side. Optional.
- `component` - `render prop` The component to render in the content pane when this layer is selected.
- `actions` - `React.Node` Specify what actions to have show up in the Actions pane using `@blueprintjs/core`'s `<MenuItem />` components.
- `noPointerEvents` - `bool` Whether this layer should accept pointer events. You may want to use this when you have multiple layers that can be active at the same time to avoid them competing with each other for clicks. For example a Bounding Box layer on top of a VideoPlayer layer may want to set this on so that click events can passthrough to the underlying VideoPlayer component.
- `alwaysOn` - `bool` Always show this layer, even if it's not selected.
- `onWithGroup` - `bool` Always show this layer if it, or one of it's sibling, or it's parent is selected.
- `getData({ store })` - `function` If you would like the rendered component of this layer to receive dynamic props, e.g. as the state of the app updates, you can implement this function. It receives as args a `store` object that represents an instance of the `global-context-store`.
- `onSelect({ store })` - `function` Code to execute when this layer is selected. It receives as args a `store` object that represents an instance of the `global-context-store`.