import React from "react";
import Wrapper from "./Wrapper";

import { AppShell, Layer } from "annotation-toolkit";
import { useStore } from "global-context-store";
import { MenuItem } from "@blueprintjs/core";

export default {
  title: "Example/Panels",
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
export const TODOActionsPanel = () => {
  return (
    <AppShell
      layers={() => (
        <Layer
          displayName="Layer"
          icon="layer"
          actions={<MenuItem></MenuItem>}
        />
      )}
    />
  );
};
