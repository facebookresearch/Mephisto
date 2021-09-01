import React from "react";
import { Navbar, Alignment, Card, Elevation, H3 } from "@blueprintjs/core";
import ContentPanel from "./panels/ContentPanel";
import LayersPanel from "./panels/LayersPanel";
import Layer from "./layers/Layer";
import cx from "classnames";
import { Button } from "@blueprintjs/core";
import { useStore } from "global-context-store";

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
              <Button
                intent={button.intent}
                key={idx + "-" + button.title}
                title={button.title}
                onClick={() => button.action && button.action()}
                icon={button.icon}
                minimal={true}
                className={"mosaic-default-control"}
              ></Button>
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

function DefaultInstructionalLayer() {
  const i = (n = 1) => `\n${new Array(n * 2).fill(" ").join("")}`;
  return (
    <Layer
      displayName="No Layers Specified"
      icon="warning-sign"
      component={() => {
        return (
          <Card className="bp3-dark" elevation={Elevation.ONE}>
            <H3>You have not specified any layers.</H3>
            <p>
              You likely left out the <code>layers</code> prop for{" "}
              <code>{"<AppShell />"}</code>.
            </p>
            <p>
              To get up and running with the <code>annotation-toolkit</code>, go
              ahead and specify one or more layers:
            </p>

            <pre>
              {`<AppShell layers={() => <>${i(
                1
              )}<Layer displayName='My First Layer' component={() => <div>First layer</div>} />` +
                `${i(
                  1
                )}<Layer displayName='My Second Layer' component={() => <div>Second layer</div>} />${i(
                  0
                )}</>} />`}
            </pre>

            <p>
              More documentation on the <code>{"<Layer />"}</code> component can
              be found{" "}
              <a
                style={{ fontWeight: "bold" }}
                target="_blank"
                href="https://github.com/facebookresearch/Mephisto/tree/main/packages/annotation-toolkit"
              >
                here
              </a>
              .
            </p>

            <hr className="bp3-menu-divider" />

            <p>
              Note: If you intentionally wanted to specify no layers and want to
              hide this prompt, write the following:
            </p>

            <pre>{"<AppShell layers={() => null} />"}</pre>
          </Card>
        );
      }}
    />
  );
}

function AppShell({
  showNavbar = false,
  layers = () => <DefaultInstructionalLayer />,
  layerButtons = [],
  showDebugPane = false,
  contextPanel: ContextPanel = () => null,
  contextHeight = "200px",
  instructionPane = null,
}) {
  const { set } = useStore();

  const portalRef = React.useRef();
  React.useEffect(() => {
    set("_unsafe.portalRef", portalRef.current);
  }, [portalRef.current]);

  return (
    <div className="full">
      <div
        style={{ position: "absolute", top: 0, bottom: 0, left: 0, right: 0 }}
        ref={portalRef}
      ></div>
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
            <Window title="Layers" buttons={layerButtons}>
              <LayersPanel layers={layers} showDebugPane={showDebugPane} />
            </Window>
          </div>
          <div
            className="mosaic-tile"
            style={{ inset: `0% 0% ${contextHeight} 300px` }}
          >
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
              <ContentPanel instructionPane={instructionPane} />
            </Window>
          </div>
          <div
            className="mosaic-tile"
            style={{ inset: `calc(100% - ${contextHeight}) 0% 0% 300px` }}
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
