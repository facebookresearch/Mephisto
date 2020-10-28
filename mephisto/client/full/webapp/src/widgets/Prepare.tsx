/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import BaseWidget from "./Base";
import { Colors, Icon, Button } from "@blueprintjs/core";
import { pluralize } from "../utils";
import cx from "classnames";
import useAxios from "axios-hooks";
import { Drawer, Classes, Position, Card } from "@blueprintjs/core";
import { Requesters, Requester } from "../models";
import { createAsync } from "../lib/Async";
import RequesterForm from "../widgets/components/RequesterForm";

const Async = createAsync<Requesters>();

export default (function PrepareWidget() {
  const [numProviders, setNumProviders] = React.useState(0);
  const [numInstalledTasks, setNumInstalledTasks] = React.useState(1);
  const [requesterDrawerOpen, setRequesterDrawerOpen] = React.useState(false);

  const requesterAsync = useAxios<Requesters>({
    url: "requesters",
  });

  return (
    <BaseWidget badge="Step 1" heading={<span>Prepare it</span>}>
      <>
        <div className="bullet">
          <div className="bp3-text-large bp3-running-text bp3-text-muted">
            <Async
              info={requesterAsync}
              onError={({ refetch }) => (
                <span>
                  <Icon icon="warning-sign" color={Colors.RED3} /> Something
                  went wrong.{" "}
                  <a onClick={() => refetch()}>
                    <strong>Try again</strong>
                  </a>
                </span>
              )}
              onLoading={() => (
                <div className="bp3-skeleton bp3-text">&nbsp; </div>
              )}
              checkIfEmptyFn={(data) => data.requesters}
              onEmptyData={() => (
                <span>
                  <Icon icon="warning-sign" color={Colors.ORANGE3} />
                  {"  "}
                  You have no accounts set up.{" "}
                  <a onClick={() => setRequesterDrawerOpen(true)}>
                    <strong>Configure</strong>
                  </a>
                </span>
              )}
              onData={({ data }) => (
                <span>
                  <Icon icon="people" /> You have{" "}
                  <a onClick={() => setRequesterDrawerOpen(true)}>
                    <strong>{data.requesters.length} requester accounts</strong>
                  </a>{" "}
                  set up
                </span>
              )}
            />
          </div>
          <Drawer
            icon="people"
            onClose={() => setRequesterDrawerOpen(false)}
            title="Requester accounts"
            autoFocus={true}
            canEscapeKeyClose={true}
            // canOutsideClickClose={true}
            enforceFocus={true}
            hasBackdrop={true}
            isOpen={requesterDrawerOpen}
            position={Position.BOTTOM}
            size={"72%"}
            usePortal={true}
          >
            <div
              className={Classes.DRAWER_BODY}
              style={{ backgroundColor: Colors.LIGHT_GRAY4 }}
            >
              <div className={Classes.DIALOG_BODY}>
                {requesterAsync[0].data && (
                  <div>
                    {requesterAsync[0].data.requesters.map((r: Requester) => (
                      <div key={r.requester_id} style={{ marginBottom: 12 }}>
                        <Card interactive={true}>
                          <Icon
                            icon={r.registered ? "tick-circle" : "issue"}
                            color={r.registered ? Colors.GREEN4 : Colors.GRAY4}
                            title={"Registered?"}
                          />
                          <span
                            style={{ margin: "0 15px" }}
                            className="bp3-tag bp3-large bp3-minimal bp3-round step-badge"
                          >
                            {r.provider_type}
                          </span>
                          <h4
                            style={{ display: "inline", marginRight: 4 }}
                            className={cx("bp3-heading", {
                              "bp3-text-muted": !r.registered,
                            })}
                          >
                            {r.requester_name}
                          </h4>{" "}
                          {!r.registered && (
                            <span>
                              &mdash; This account still needs to be registered.
                            </span>
                          )}
                        </Card>
                      </div>
                    ))}
                    <div style={{ marginTop: 15 }}>
                      <RequesterForm
                        onFinish={() => {
                          setRequesterDrawerOpen(false);
                          window.location.reload();
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Drawer>
        </div>
        <div className="bullet">
          <div className="bp3-text-large bp3-running-text bp3-text-muted">
            <Icon icon={numInstalledTasks === 1 ? "layer" : "layers"} /> You
            have{" "}
            <strong>
              {numInstalledTasks} task{" "}
              {pluralize(numInstalledTasks, "template")}
            </strong>
            {"  "}
            available to use
          </div>
        </div>
      </>
    </BaseWidget>
  );
} as React.FC);
