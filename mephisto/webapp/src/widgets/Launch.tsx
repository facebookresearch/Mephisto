/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";
import { TaskRun, RunningTasks } from "../models";
import { task_runs__running } from "../mocks";
import {
  Colors,
  Icon,
  Drawer,
  Position,
  Classes,
  Card,
  Button,
  Intent,
  Toaster,
} from "@blueprintjs/core";
import { createAsync, mockRequest } from "../lib/Async";
import TaskRunSummary from "./TaskRunSummary";
import BlueprintSelect from "./components/BlueprintSelect";
import ArchitectSelect from "./components/ArchitectSelect";
import RequesterSelect from "./components/RequesterSelect";
import { toaster } from "../lib/toaster";
import { launchTask } from "../service";
import OptionsForm from "./components/OptionsForm";

const Async = createAsync<RunningTasks>();
const LaunchInfoAsync = createAsync<any>();
const RequesterInfoAsync = createAsync<any>();
const DefaultTaskInfoAsync = createAsync<any>();

export default (function LaunchWidget() {
  // const runningTasksAsync = mockRequest<RunningTasks>(task_runs__running);
  const runningTasksAsync = useAxios({ url: "task_runs/running" });

  return (
    <BaseWidget badge="Step 2" heading={<span>Launch it</span>}>
      <Async
        info={runningTasksAsync}
        onLoading={() => (
          <div className="bp3-non-ideal-state bp3-skeleton">
            <div
              className="bp3-non-ideal-state-visual"
              style={{ fontSize: 20 }}
            >
              <span className="bp3-icon bp3-icon-clean"></span>
            </div>
            <div>You have no tasks running.</div>
          </div>
        )}
        onData={({ data }) => (
          <div>
            {data.task_runs.map((run: TaskRun) => (
              <TaskRunSummary key={run.task_run_id} run={run} />
            ))}
          </div>
        )}
        checkIfEmptyFn={(data) => data.task_runs}
        onEmptyData={() => (
          <div className="bp3-non-ideal-state">
            <div
              className="bp3-non-ideal-state-visual"
              style={{ fontSize: 20 }}
            >
              <span className="bp3-icon bp3-icon-clean"></span>
            </div>
            <div>You have no tasks running.</div>
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
      />
      <div>
        <div style={{ textAlign: "center", marginTop: 15 }}>
          <LaunchForm />
        </div>
      </div>
    </BaseWidget>
  );
} as React.FC);

function LaunchForm() {
  const [openForm, setOpenForm] = React.useState(false);
  const launchInfo = useAxios({ url: "launch/options" });
  const requesterInfo = useAxios({
    url: "requesters",
  });
  const defaultTaskInfo = useAxios({
    url: "task_runs/options",
  });

  const [params, addToParams] = React.useReducer((state, params) => {
    let nextState;
    if (params === "CLEAR_ALL") {
      nextState = {};
    } else if (params === "CLEAR_bp") {
      nextState = Object.keys(state)
        .filter((key) => !key.startsWith("bp|"))
        .reduce((obj: any, key: string) => {
          obj[key] = state[key];
          return obj;
        }, {});
    } else if (params === "CLEAR_arch") {
      nextState = Object.keys(state)
        .filter((key) => !key.startsWith("arch|"))
        .reduce((obj: any, key: string) => {
          obj[key] = state[key];
          return obj;
        }, {});
    } else if (params === "CLEAR_task") {
      nextState = Object.keys(state)
        .filter((key) => !key.startsWith("task|"))
        .reduce((obj: any, key: string) => {
          obj[key] = state[key];
          return obj;
        }, {});
    } else {
      nextState = { ...state, ...params };
    }
    return nextState;
  }, {});

  return (
    <div>
      <button className="bp3-button" onClick={() => setOpenForm(true)}>
        Launch a task
      </button>
      <Drawer
        icon="people"
        onClose={() => setOpenForm(false)}
        title="Launch a task"
        autoFocus={true}
        canEscapeKeyClose={false}
        canOutsideClickClose={false}
        enforceFocus={true}
        hasBackdrop={true}
        isOpen={openForm}
        position={Position.RIGHT}
        size={"50%"}
        usePortal={true}
      >
        <div
          className={Classes.DRAWER_BODY}
          style={{ backgroundColor: Colors.LIGHT_GRAY4 }}
        >
          <div className={Classes.DIALOG_BODY}>
            <h2>Step 1. Choose a Task Blueprint</h2>
            <p className="bp3-text-muted">
              A blueprint defines the task that will be run &amp; its associated
              configuration parameters.
            </p>
            <LaunchInfoAsync
              info={launchInfo}
              onLoading={() => <span>Loading...</span>}
              onData={({ data }) => (
                <div>
                  <BlueprintSelect
                    data={data.blueprint_types}
                    onUpdate={(data: any) => addToParams(data)}
                  />
                </div>
              )}
              onError={() => <span>Error</span>}
            />

            <h2>Step 2. Choose an Architect</h2>
            <p className="bp3-text-muted">
              An architect manages the deployment target of your task.
            </p>
            <LaunchInfoAsync
              info={launchInfo}
              onLoading={() => <span>Loading...</span>}
              onData={({ data }) => (
                <div>
                  <ArchitectSelect
                    data={data.architect_types}
                    onUpdate={(data: any) => {
                      addToParams(data);
                    }}
                  />
                </div>
              )}
              onError={() => <span>Error</span>}
            />
            <h2>Step 3. Choose a Requester</h2>
            <p className="bp3-text-muted">
              A requester is the service account that will run your task.
            </p>
            <RequesterInfoAsync
              info={requesterInfo}
              onLoading={() => <span>Loading...</span>}
              onData={({ data }) => (
                <div>
                  <RequesterSelect
                    data={data.requesters.filter((r: any) => r.registered)}
                    onUpdate={(data: any) => {
                      addToParams(data);
                    }}
                  />
                </div>
              )}
              onError={() => <span>Error</span>}
            />
            <h2>Step 4. Final Task Options</h2>
            <DefaultTaskInfoAsync
              info={defaultTaskInfo}
              onLoading={() => <span>Loading...</span>}
              onData={({ data }) => (
                <div>
                  <OptionsForm
                    prefix="task"
                    options={data.options}
                    onUpdate={(data: any) => addToParams(data)}
                  />
                </div>
              )}
              onError={() => <span>Error</span>}
            />

            <Button
              onClick={() => {
                let validated =
                  params.blueprint !== undefined &&
                  params.architect !== undefined &&
                  params.requester !== undefined;

                const allTaskParamsFilled = Object.entries(params).reduce(
                  (allFilled, [key, value]) => {
                    if (key.startsWith("task|")) {
                      return allFilled && value !== null;
                    } else {
                      return allFilled;
                    }
                  },
                  true
                );

                validated = validated && allTaskParamsFilled;

                if (validated) {
                  addToParams("CLEAR_ALL");

                  launchTask(params)
                    .then(() => {
                      setOpenForm(false);

                      toaster.dismiss("loading-msg");
                      toaster.show({
                        message: "Launched!",
                        icon: "cloud-upload",
                        intent: Intent.SUCCESS,
                        timeout: 3000,
                      });
                    })
                    .catch(() => {
                      // TODO: Handle error, also check payload in case
                      // it specifies an error, e.g. ensure that
                      // payload.status === 'success'
                    });

                  toaster.show(
                    {
                      message:
                        "Launching task... Please wait this may take a while.",
                      icon: "cloud-upload",
                      intent: Intent.NONE,
                      timeout: 40000,
                    },
                    "loading-msg"
                  );
                } else {
                  toaster.show({
                    message:
                      "Error: Must select Blueprint + Architect + Requester and fill all task params",
                    icon: "cloud-upload",
                    intent: Intent.DANGER,
                    timeout: 2000,
                  });
                }
              }}
              large
              icon="cloud-upload"
              intent={Intent.SUCCESS}
              style={{ margin: "20px auto 0" }}
            >
              Launch
            </Button>
          </div>
        </div>
      </Drawer>
    </div>
  );
}
