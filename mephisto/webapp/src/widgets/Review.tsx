import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";
import Async, { mockRequest } from "../lib/Async";
import { Icon, Colors } from "@blueprintjs/core";

export default (function ReviewWidget() {
  const reviewAsync = useAxios({
    url: "task_runs/reviewable"
  });

  return (
    <BaseWidget badge="Step 3" heading={<span>Review it</span>}>
      <Async
        info={reviewAsync}
        onLoading={() => (
          <div className="bp3-skeleton">
            <div className="bp3-non-ideal-state">
              <div
                className="bp3-non-ideal-state-visual"
                style={{ fontSize: 20 }}
              >
                <span className="bp3-icon bp3-icon-inbox-search"></span>
              </div>
              <div>You have no work to review.</div>
            </div>
          </div>
        )}
        onError={({ refetch }) => (
          <span>
            <Icon icon="warning-sign" color={Colors.RED3} /> Something went
            wrong.{" "}
            <a onClick={() => refetch()}>
              <strong>Try again</strong>
            </a>
          </span>
        )}
        onData={({ data }) => <span>{JSON.stringify(data)}</span>}
        checkIfEmptyFn={(data: any) => data.task_runs}
        onEmptyData={() => (
          <div>
            <div className="bp3-non-ideal-state">
              <div
                className="bp3-non-ideal-state-visual"
                style={{ fontSize: 20 }}
              >
                <span className="bp3-icon bp3-icon-inbox-search"></span>
              </div>
              <div>You have no work to review.</div>
            </div>
          </div>
        )}
      />
    </BaseWidget>
  );
} as React.FC);
