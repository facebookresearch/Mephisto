/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { InReviewFileModal } from "components/InReviewFileModal/InReviewFileModal";
import TasksHeader from "components/TasksHeader/TasksHeader";
import WorkerOpinionCollapsable from "components/WorkerOpinionCollapsable/WorkerOpinionCollapsable";
import { setPageTitle } from "pages/TaskPage/helpers";
import * as React from "react";
import { useEffect } from "react";
import { Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { getTaskWorkerOpinions } from "requests/tasks";
import "./TaskWorkerOpinionsPage.css";

type ParamsType = {
  id: string;
};

type TaskWorkerOpinionsPagePropsType = {
  setErrors: Function;
};

function TaskWorkerOpinionsPage(props: TaskWorkerOpinionsPagePropsType) {
  const params = useParams<ParamsType>();

  const [taskWorkerOpinions, setTaskWorkerOpinions] = React.useState<
    TaskWorkerOpinionsType
  >(null);
  const [loading, setLoading] = React.useState(false);
  const [opinionsVisibility, setOpinionsVisibility] = React.useState<boolean>(
    true
  );
  const [inReviewFileModalShow, setInReviewFileModalShow] = React.useState<
    boolean
  >(false);
  const [inReviewFileModalData, setInReviewFileModalData] = React.useState<
    InReviewFileModalDataType
  >({});

  function onError(errorResponse: ErrorResponseType | null) {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  }

  function onClickOnWorkerOpinionAttachment(
    file: WorkerOpinionAttachmentType,
    workerOpinion: TaskWorkerOpinionType
  ) {
    const unitDataFolderStartIndex = workerOpinion.unit_data_folder.indexOf(
      "data/data"
    );
    const unitDataFolder = workerOpinion.unit_data_folder.slice(
      unitDataFolderStartIndex
    );

    setInReviewFileModalData({
      fieldname: file.fieldname,
      filename: file.filename,
      requestByFilename: true,
      title: file.filename,
      unitDataFolder: unitDataFolder,
      unitId: workerOpinion.unit_id,
    });
    setInReviewFileModalShow(true);
  }

  // Effects
  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Worker Opinions");

    if (taskWorkerOpinions === null) {
      getTaskWorkerOpinions(
        params.id,
        setTaskWorkerOpinions,
        setLoading,
        onError,
        null
      );
    }
  }, []);

  useEffect(() => {
    if (taskWorkerOpinions) {
      // Update title with current task name
      setPageTitle(
        `Mephisto - Task Worker Opinions - ${taskWorkerOpinions.task_name}`
      );
    }
  }, [taskWorkerOpinions]);

  return (
    <div className={"task-worker-opinions"}>
      {/* Header */}
      <TasksHeader />

      {!loading && taskWorkerOpinions && (
        // Task name
        <div className={"header"}>
          <div className={"task-name"}>
            Task: {taskWorkerOpinions.task_name}
          </div>

          {taskWorkerOpinions?.worker_opinions && (
            <>
              <div>{taskWorkerOpinions.worker_opinions.length} opinions</div>

              <button
                className={"btn btn-primary btn-sm"}
                onClick={() => setOpinionsVisibility(!opinionsVisibility)}
                type={"button"}
              >
                {opinionsVisibility ? "Close" : "Open"} all
              </button>
            </>
          )}
        </div>
      )}

      <div className={"content"}>
        {/* Preloader when we request task worker opinions */}
        {loading ? (
          <div className={"loading"}>
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : (
          // Worker Opinions
          taskWorkerOpinions?.worker_opinions?.map(
            (workerOpinion: TaskWorkerOpinionType, index: number) => {
              const title = (
                <span className={"task-worker-opinion-title"}>
                  <span className={"task-worker-opinion-title-id"}>
                    Worker ID:
                    <span className={"task-worker-opinion-title-id-value"}>
                      {workerOpinion.worker_id}
                    </span>
                  </span>
                  <span className={"task-worker-opinion-title-id"}>
                    Unit ID:
                    <span className={"task-worker-opinion-title-id-value"}>
                      {workerOpinion.unit_id}
                    </span>
                  </span>
                </span>
              );

              return (
                <WorkerOpinionCollapsable
                  className={"task-worker-opinion"}
                  data={workerOpinion.data}
                  key={`task-worker-opinion-${index}`}
                  onClickOnAttachment={(file: WorkerOpinionAttachmentType) => {
                    onClickOnWorkerOpinionAttachment(file, workerOpinion);
                  }}
                  open={opinionsVisibility}
                  title={title}
                />
              );
            }
          )
        )}
      </div>

      {/* Modal to show preview of attachments */}
      <InReviewFileModal
        show={inReviewFileModalShow}
        setShow={setInReviewFileModalShow}
        data={inReviewFileModalData}
        setData={setInReviewFileModalData}
      />
    </div>
  );
}

export default TaskWorkerOpinionsPage;
