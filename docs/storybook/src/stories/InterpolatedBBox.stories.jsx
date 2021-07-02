import React from "react";
import Wrapper from "./Wrapper";

import { AppShell, Layer } from "annotation-toolkit";
import { useStore } from "global-context-store";
import { MenuItem } from "@blueprintjs/core";

export default {
  title: "Example/4. Interpolated BBox",
  component: AppShell,
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
};

export const BasicBox = () => {
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
