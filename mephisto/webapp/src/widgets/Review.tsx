import React from "react";
import BaseWidget from "./Base";

export default (function ReviewWidget() {
  return (
    <BaseWidget badge="Step 3" heading={<span>Review it</span>}>
      <div>
        <div className="bp3-non-ideal-state">
          <div className="bp3-non-ideal-state-visual" style={{ fontSize: 20 }}>
            <span className="bp3-icon bp3-icon-inbox-search"></span>
          </div>
          <div>You have no work to review.</div>
        </div>
      </div>
    </BaseWidget>
  );
} as React.FC);
