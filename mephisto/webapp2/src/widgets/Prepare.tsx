import React from "react";
import BaseWidget from "./Base";
import { Colors } from "@blueprintjs/core";
import { pluralize } from "../utils";
import cx from "classnames";
import useAxios from "axios-hooks";

export default (function PrepareWidget() {
  const [numProviders, setNumProviders] = React.useState(0);
  const [numInstalledTasks, setNumInstalledTasks] = React.useState(1);

  const [{ data, loading, error }, refetch] = useAxios({
    url: "requesters",
    params: "test"
  });

  return (
    <BaseWidget badge="Step 1" heading={<span>Prepare it</span>}>
      <>
        <div className="bullet">
          <div className="bp3-text-large bp3-running-text bp3-text-muted">
            {error ? (
              <span>
                <span
                  style={{ color: Colors.RED3 }}
                  className="bp3-icon-small bp3-icon-warning-sign"
                ></span>{" "}
                Something went wrong.{" "}
                <a onClick={() => refetch()}>
                  <strong>Try again</strong>
                </a>
              </span>
            ) : loading ? (
              <div className="bp3-skeleton bp3-text">&nbsp; </div>
            ) : data.requesters.length === 0 ? (
              <span>
                <span
                  style={{ color: Colors.ORANGE3 }}
                  className="bp3-icon-small bp3-icon-warning-sign"
                ></span>
                {"  "}
                You have no accounts set up.{" "}
                <a>
                  <strong>Configure</strong>
                </a>
              </span>
            ) : (
              <span>
                <span className="bp3-icon-small bp3-icon-people"></span> You
                have <strong>{data.requesters.length}</strong> crowdprovider
                accounts
              </span>
            )}
            {/* 
            {numProviders === 0 ? (
              <span>
                <span
                  style={{ color: Colors.ORANGE3 }}
                  className="bp3-icon-small bp3-icon-warning-sign"
                ></span>
                {"  "}
                You have no accounts set up.{" "}
                <a>
                  <strong>Configure</strong>
                </a>
              </span>
            ) : !numProviders ? (
              <div className="bp3-skeleton bp3-text">&nbsp; </div>
            ) : (
              <span>
                <span className="bp3-icon-small bp3-icon-people"></span> You
                have <strong>5</strong> crowdprovider accounts
              </span>
            )} */}
          </div>
        </div>
        <div className="bullet">
          <div className="bp3-text-large bp3-running-text bp3-text-muted">
            <span
              className={cx(
                "bp3-icon-small",
                numInstalledTasks === 1 ? "bp3-icon-layer" : "bp3-icon-layers"
              )}
            ></span>{" "}
            You have{" "}
            <strong>
              {numInstalledTasks} {pluralize(numInstalledTasks, "task")}
            </strong>
            {"  "}
            available to use
          </div>
        </div>
      </>
    </BaseWidget>
  );
} as React.FC);
