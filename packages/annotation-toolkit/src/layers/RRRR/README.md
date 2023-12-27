<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

This is a fork of the project from https://github.com/mockingbot/react-resizable-rotatable-draggable

The fork:
- Removes the dependency on styled-components, dropping the StyledRect component and moving the styles to "react-rect.css".
- Allows for a `document` prop to be passed in to change where event handlers are attached to (good for iframe usage)