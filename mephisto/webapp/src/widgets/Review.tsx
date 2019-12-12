import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";

export default (function ReviewWidget() {
  const [{ data, loading, error }, refetch] = useAxios({
    url: "task_runs/reviewable"
  });

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
