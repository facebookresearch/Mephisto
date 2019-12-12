import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";
import Async from "../lib/Async";

export default (function ReviewWidget() {
  const info = useAxios({
    url: "error",
    delayed: true
  });

  return (
    <BaseWidget badge="Step 3" heading={<span>Review it</span>}>
      <Async
        info={info}
        onLoading={() => <span>Loading...</span>}
        onError={({ error }) => <span>{JSON.stringify(error)}</span>}
        onData={({ data }) => <span>{JSON.stringify(data)}</span>}
      />
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
