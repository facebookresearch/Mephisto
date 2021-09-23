import React from "react";
import Wrapper from "./Wrapper";

import { AppShell, Layer } from "@annotated/shell";
import { MenuItem } from "@blueprintjs/core";

export default {
  title: "Example/2. Panels",
  component: AppShell,
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
};

export const DebugPanel = () => {
  return <AppShell showDebugPane={true} />;
};
export const ActionsPanel = () => {
  return (
    <AppShell
      layers={() => (
        <Layer
          alwaysOn
          displayName="Layer"
          icon="layer"
          component={() => null}
          actions={() => (
            <MenuItem
              text="Sample menu item"
              icon="notifications"
              onClick={() => {
                alert("clicked!");
              }}
            />
          )}
        />
      )}
    />
  );
};

// TODO: Add other actions panel stuff, such as HorizontalMenu, and behavior
// with complex layer activation states such as onWithGroup and alwaysOn
