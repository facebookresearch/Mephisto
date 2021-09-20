import React from "react";
import Wrapper from "./Wrapper";
import { AppShell, Layer } from "@annotated/shell";
import { useStore } from "global-context-store";
import { Card, Elevation } from "@blueprintjs/core";

export default {
  title: "Example/1. Layers",
  component: AppShell,
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
};

export const NoLayers = () => {
  return <AppShell />;
};
export const SingleLayer = () => (
  <AppShell
    layers={() => (
      <Layer
        displayName="My First Layer"
        icon="layer"
        component={() => (
          <Card elevation={Elevation.TWO}>Contents for my first layer</Card>
        )}
      />
    )}
  />
);
export const SingleLayerCustomIcon = () => {
  return (
    <AppShell
      layers={() => (
        <Layer
          displayName="My First Layer"
          icon="widget"
          component={() => (
            <Card elevation={Elevation.TWO}>
              This layer uses the "widget" icon from the{" "}
              <a href="https://blueprintjs.com/docs/#icons" target="_blank">
                BlueprintJS icon set
              </a>
              .
            </Card>
          )}
        />
      )}
    />
  );
};
SingleLayerCustomIcon.storyName = "Single Layer (w/ custom icon)";

export const SingleLayerCustomSecondaryIcon = () => {
  return (
    <AppShell
      layers={() => (
        <Layer
          displayName="My First Layer"
          icon="widget"
          secondaryIcon="link"
          component={() => (
            <Card elevation={Elevation.TWO}>
              This layer uses the "widget" icon and the "link" icon from the{" "}
              <a href="https://blueprintjs.com/docs/#icons" target="_blank">
                BlueprintJS icon set
              </a>
              .
            </Card>
          )}
        />
      )}
    />
  );
};
SingleLayerCustomSecondaryIcon.storyName = "Single Layer (w/ secondary icon)";

export const SingleLayerSelectedByDefault = () => {
  const { set } = useStore();
  React.useEffect(() => {
    set(["selectedLayer"], ["My First Layer"]);
  }, []);
  return (
    <AppShell
      layers={() => (
        <Layer
          displayName="My First Layer"
          icon="layer"
          component={() => (
            <Card elevation={Elevation.TWO}>Contents for my first layer</Card>
          )}
        />
      )}
    />
  );
};
SingleLayerSelectedByDefault.storyName = "Single Layer (auto-selected)";

export const MultipleLayers = () => {
  return (
    <AppShell
      layers={() => (
        <>
          <Layer
            displayName="My First Layer"
            icon="layer"
            component={() => (
              <Card elevation={Elevation.TWO}>Contents for my first layer</Card>
            )}
          />
          <Layer
            displayName="My Second Layer"
            icon="layer"
            component={() => (
              <Card elevation={Elevation.TWO}>
                Contents for my second layer
              </Card>
            )}
          />
        </>
      )}
    />
  );
};

export const NestedLayers = () => {
  return (
    <AppShell
      layers={() => (
        <>
          <Layer
            displayName="My Parent Layer"
            icon="layer"
            component={() => (
              <Card elevation={Elevation.TWO}>
                Contents for my parent layer
              </Card>
            )}
          >
            <Layer
              displayName="My Child Layer"
              icon="layer"
              component={() => (
                <Card elevation={Elevation.TWO}>
                  Contents for my child layer
                </Card>
              )}
            />
          </Layer>
        </>
      )}
    />
  );
};

export const DeeplyNestedLayers = () => {
  return (
    <AppShell
      layers={() => (
        <>
          <Layer
            displayName="My Grandparent Layer"
            icon="layer"
            component={() => (
              <Card elevation={Elevation.TWO}>
                Contents for my grandparent layer
              </Card>
            )}
          >
            <Layer
              displayName="My Parent Layer"
              icon="layer"
              component={() => (
                <Card elevation={Elevation.TWO}>
                  Contents for my parent layer
                </Card>
              )}
            >
              <Layer
                displayName="My Child Layer"
                icon="layer"
                component={() => (
                  <Card elevation={Elevation.TWO}>
                    Contents for my child layer
                  </Card>
                )}
              />
            </Layer>
          </Layer>
        </>
      )}
    />
  );
};

export const TODOAlwaysOn = () => null;
export const TODOHideName = () => null;
export const TODONoPointerEvents = () => null;
export const TODOOnWithGroup = () => null;
export const TODOOnSelect = () => null;
