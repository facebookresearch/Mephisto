import { Navbar, Alignment } from "@blueprintjs/core";
import React from "react";
import ContentPanel from "./panels/ContentPanel";
import LayersPanel from "./panels/LayersPanel";
import cx from "classnames";

function Window({ title, children, buttons, bodyClassNames = [] }) {
  return (
    <div className="mosaic-window">
      <div className="mosaic-window-toolbar">
        <div title={title} className="mosaic-window-title">
          {title}
        </div>
        {buttons ? (
          <div className="mosaic-window-controls bp3-button-group">
            {buttons.map((button, idx) => (
              <button
                key={idx + "-" + button.title}
                title={button.title}
                className={
                  "mosaic-default-control bp3-button bp3-minimal bp3-icon-" +
                  button.icon
                }
              ></button>
            ))}
          </div>
        ) : null}
      </div>
      <div className={cx("mosaic-window-body", ...bodyClassNames)}>
        {children}
      </div>
    </div>
  );
}

function AppShell({
  showNavbar = false,
  layers,
  showDebugPane = false,
  contextPanel: ContextPanel = () => null,
}) {
  return (
    <div className="full">
      {showNavbar ? (
        <Navbar className="bp3-dark">
          <Navbar.Group align={Alignment.LEFT}>
            <Navbar.Heading>Mephisto Studio</Navbar.Heading>
            <Navbar.Divider />
            {/* <Button className="bp3-minimal" icon="home" text="Home" />
            <Button className="bp3-minimal" icon="document" text="Files" /> */}
          </Navbar.Group>
        </Navbar>
      ) : null}
      <div
        className={cx(
          "mosaic-blueprint-theme",
          "mosaic",
          showNavbar ? "mosaic-w-navbar" : ""
        )}
      >
        <div className="mosaic-root">
          <div
            className="mosaic-tile"
            style={{ inset: "0% calc(100% - 300px) 0% 0%" }}
          >
            <Window title="Layers">
              <LayersPanel layers={layers} showDebugPane={showDebugPane} />
            </Window>
          </div>
          <div className="mosaic-tile" style={{ inset: "0% 0% 200px 300px" }}>
            <Window
              title="Content"
              bodyClassNames={["grid-background"]}
              buttons={[
                {
                  icon: "settings",
                  title: "Settings",
                  action: () => {},
                },
              ]}
            >
              <ContentPanel />
            </Window>
          </div>
          <div
            className="mosaic-tile"
            style={{ inset: "calc(100% - 200px) 0% 0% 300px" }}
          >
            <Window title="Context">
              <ContextPanel />
            </Window>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AppShell;
