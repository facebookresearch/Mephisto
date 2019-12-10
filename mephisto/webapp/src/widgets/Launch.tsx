import React from "react";
import BaseWidget from "./Base";

export default (function LaunchWidget() {
  return (
    <BaseWidget badge="Step 2" heading={<span>Launch it</span>}>
      <div>
        <div className="bp3-non-ideal-state">
          <div className="bp3-non-ideal-state-visual" style={{ fontSize: 20 }}>
            <span className="bp3-icon bp3-icon-clean"></span>
          </div>
          <div>You have no tasks running.</div>
          <button className="bp3-button ">Launch a task</button>
        </div>
      </div>
    </BaseWidget>
  );
} as React.FC);
