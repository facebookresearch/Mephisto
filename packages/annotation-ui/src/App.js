import { Navbar, Alignment } from "@blueprintjs/core";
import React from "react";
import ContentPanel from "./panels/ContentPanel";
import ContextPanel from "./panels/ContextPanel";
import LayersPanel from "./panels/LayersPanel";
import cx from "classnames";

function Window({ title, children, buttons }) {
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
      <div className="mosaic-window-body">{children}</div>
    </div>
  );
}

function App({ showNavbar = false }) {
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
              <LayersPanel />
            </Window>
          </div>
          <div className="mosaic-tile" style={{ inset: "0% 0% 200px 300px" }}>
            <Window
              title="Content"
              buttons={[
                {
                  icon: "settings",
                  title: "Exchange",
                  action: () => {
                    alert("hi");
                  },
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

export default App;
