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
  Toaster
} from "@blueprintjs/core";
import { createAsync, mockRequest } from "../lib/Async";
import TaskRunSummary from "./TaskRunSummary";
import BlueprintSelect from "./components/BlueprintSelect";
import ArchitectSelect from "./components/ArchitectSelect";
import { toaster } from "../lib/toaster";

const Async = createAsync<RunningTasks>();
const LaunchInfoAsync = createAsync<any>();

export default (function LaunchWidget() {
  const runningTasksAsync = mockRequest<RunningTasks>(task_runs__running);

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
        checkIfEmptyFn={data => data.task_runs}
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

  const [params, addToParams] = React.useReducer((state, params) => {
    return { ...state, ...params };
  }, {});

  return (
    <div>
      <button className="bp3-button" onClick={() => setOpenForm(true)}>
        [TODO] Launch a task
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
            <Button
              onClick={() => {
                const validated = true;

                if (validated) {
                  setOpenForm(false);
                  toaster.show({
                    message: "Launching task...",
                    icon: "cloud-upload",
                    intent: Intent.NONE,
                    timeout: 2000
                  });
                  setTimeout(
                    () =>
                      toaster.show({
                        message: "Launched!",
                        icon: "cloud-upload",
                        intent: Intent.SUCCESS,
                        timeout: 2000
                      }),
                    1000
                  );
                } else {
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
