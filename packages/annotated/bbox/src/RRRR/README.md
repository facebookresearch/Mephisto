This is a fork of the project from https://github.com/mockingbot/react-resizable-rotatable-draggable

The fork:
- Removes the dependency on styled-components, dropping the StyledRect component and moving the styles to "react-rect.css".
- Allows for a `document` prop to be passed in to change where event handlers are attached to (good for iframe usage)