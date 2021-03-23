import React, { useContext } from "react";
import cx from "classnames";
import { Context } from "../model/Store";

const LayerContext = React.createContext({ stack: [] });

function Layer({
  displayName,
  icon,
  secondaryIcon = "",
  children,
  component,
  actions = null,
  noPointerEvents,
  alwaysOn = false,
  onWithGroup,
}) {
  const [expanded, setExpanded] = React.useState(true);
  const { state, dispatch, set, get } = useContext(Context);
  const layerContext = React.useContext(LayerContext);
  const layerStack = [...layerContext.stack, displayName];

  const layerId = layerStack.join("|");
  const path = ["layers", layerId];
  const isRegistered = !!get(path);
  React.useEffect(() => {
    if (!isRegistered) {
      set(path, {
        component,
        actions,
        alwaysOn,
        onWithGroup,
        id: layerId,
        noPointerEvents,
      });
    }
  }, [isRegistered]);

  const handleSelect = React.useCallback(
    function (name) {
      set("selectedLayer", name);
    },
    [dispatch]
  );

  const isSelected = state.selectedLayer
    ? layerId === state.selectedLayer.join("|")
    : false;
  const depth = layerStack.length - 1;

  return (
    <LayerContext.Provider value={{ stack: layerStack }}>
      <li
        className={cx("bp3-tree-node", {
          "bp3-tree-node-selected": isSelected,
          "bp3-tree-node-expanded": expanded,
        })}
      >
        <div
          onClick={() => {
            handleSelect(layerStack);
          }}
          className={`bp3-tree-node-content bp3-tree-node-content-${depth}`}
        >
          <span
            onClick={() => setExpanded(!expanded)}
            className={cx(
              expanded ? "bp3-tree-node-caret-open" : "",
              children ? "bp3-tree-node-caret" : "bp3-tree-node-caret-none",
              "bp3-icon-standard"
            )}
          ></span>
          {icon ? (
            <span
              className={cx(
                "bp3-tree-node-icon bp3-icon-standard",
                "bp3-icon-" + icon
              )}
            ></span>
          ) : null}
          <span className="bp3-tree-node-label">{displayName}</span>
          <span
            className={cx(
              "bp3-tree-node-secondary-label bp3-icon-standard",
              "bp3-icon-" + secondaryIcon
            )}
          ></span>
        </div>
        {children && expanded ? (
          <ul className="bp3-tree-node-list">{children}</ul>
        ) : null}
      </li>
    </LayerContext.Provider>
  );
}

export default Layer;
