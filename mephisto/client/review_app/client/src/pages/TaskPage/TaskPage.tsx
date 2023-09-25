/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// TODO: Find the way to import it dynamically
// import { TaskFrontend } from 'components/mnist_core_components_copied';
import { ReviewType } from 'consts/review';
import cloneDeep from 'lodash/cloneDeep';
import * as React from 'react';
import { useEffect } from 'react';
import { Button, Spinner, Table } from 'react-bootstrap';
import JSONPretty from 'react-json-pretty';
import { useNavigate, useParams } from 'react-router-dom';
import {
  postQualificationGrantWorker,
  postQualificationRevokeWorker,
} from 'requests/qualifications';
import { getStats } from 'requests/stats';
import { getTask, getTaskWorkerUnitsIds } from 'requests/tasks';
import {
  getUnits,
  getUnitsDetails,
  postUnitsApprove,
  postUnitsReject,
  postUnitsSoftReject,
} from 'requests/units';
import { postWorkerBlock } from 'requests/workers';
import urls from 'urls';
import { setPageTitle, updateModalState } from './helpers';
import {
  APPROVE_MODAL_DATA_STATE,
  DEFAULT_MODAL_STATE_VALUE,
  REJECT_MODAL_DATA_STATE,
  SOFT_REJECT_MODAL_DATA_STATE,
} from './modalData';
import ReviewModal from './ReviewModal/ReviewModal';
import TaskHeader from './TaskHeader/TaskHeader';
import './TaskPage.css';


const MNIST_URL = process.env.REACT_APP__MNIST_URL || 'http://localhost:3000';


const defaultStats = {
  total_count: null,
  reviewed_count: 0,
  approved_count: 0,
  rejected_count: 0,
  soft_rejected_count: 0,
}


type UnitDetailsMapType = {[key: string]: UnitType & UnitDetailsType};


type ParamsType = {
  id: string;
};


interface PropsType {
  setErrors: Function;
}


function TaskPage(props: PropsType) {
  const params = useParams<ParamsType>();
  const navigate = useNavigate();

  const iframeRef = React.useRef(null);

  const [iframeLoaded, setIframeLoaded] = React.useState<boolean>(false);
  const [task, setTask] = React.useState<TaskType>(null);
  const [units, setUnits] = React.useState<Array<UnitType>>(null);
  const [loading, setLoading] = React.useState(false);

  const [modalShow, setModalShow] = React.useState<boolean>(false);
  const [modalData, setModalData] = React.useState<ModalDataType>(
    cloneDeep(APPROVE_MODAL_DATA_STATE)
  );

  const [modalState, setModalState] = React.useState<ModalStateType>(
    cloneDeep(DEFAULT_MODAL_STATE_VALUE)
  );

  const [taskStats, setTaskStats] = React.useState<TaskStatsType>(defaultStats);
  const [workerStats, setWorkerStats] = React.useState<WorkerStatsType>(defaultStats);
  const [workerUnits, setWorkerUnits] = React.useState<Array<[number, number[]]>>(null);
  const [unitsOnReview, setUnitsOnReview] = React.useState<[number, number[]]>(null);
  const [currentWorkerOnReview, setCurrentWorkerOnReview] = React.useState<number>(null);
  const [currentUnitOnReview, setCurrentUnitOnReview] = React.useState<number>(null);
  const [unitDetails, setUnitDetails] = React.useState<UnitDetailsType[]>(null);
  const [unitDetailsMap, setUnitDetailsMap] = React.useState<UnitDetailsMapType>({});

  const [finishedTask, setFinishedTask] = React.useState<boolean>(false);

  const onGetTaskWorkerUnitsIdsSuccess = (workerUnitsIds: WorkerUnitIdType[]) => {
    setWorkerUnits(() => {
      const workerUnitsMap = {};

      workerUnitsIds.forEach((item: WorkerUnitIdType) => {
        let prevValue = workerUnitsMap[item.worker_id] || [];
        prevValue.push(item.unit_id);
        workerUnitsMap[item.worker_id] = prevValue;
      });

      let sortedValue = [];
      for (let i in workerUnitsMap) {
          sortedValue.push([Number(i), workerUnitsMap[i]]);
      }

      // Sort workers by number of their units
      sortedValue.sort((a: [number, number[]], b: [number, number[]]) => {
        return a[1].length < b[1].length ? 1 : -1;
      });

      return sortedValue;
    });
  };

  const onApproveClick = () => {
    const initData = cloneDeep(APPROVE_MODAL_DATA_STATE);

    initData.applyToNext = false;
    initData.form = modalState.approve.form;
    initData.applyToNextUnitsCount = unitsOnReview[1].length;

    setModalShow(true);
    setModalData(initData);
  };

  const onSoftRejectClick = () => {
    const initData = cloneDeep(SOFT_REJECT_MODAL_DATA_STATE);

    initData.applyToNext = false;
    initData.form = modalState.softReject.form;
    initData.applyToNextUnitsCount = unitsOnReview[1].length;

    setModalShow(true);
    setModalData(initData);
  };

  const onRejectClick = () => {
    const initData = cloneDeep(REJECT_MODAL_DATA_STATE);

    initData.applyToNext = false;
    initData.form = modalState.reject.form;
    initData.applyToNextUnitsCount = unitsOnReview[1].length;

    setModalShow(true);
    setModalData(initData);
  };

  const setNextUnit = () => {
    let firstWrokerUnits = workerUnits[0];

    // If no Workers left (in case if we review multiple Units)
    if (!firstWrokerUnits) {
      setFinishedTask(true);
      return;
    }

    if (firstWrokerUnits[1].length === 0) {
      workerUnits.shift();

      // If no Worker Units left (in case if we review Units one by one)
      if (workerUnits.length === 0) {
        setFinishedTask(true);
        return;
      }
      firstWrokerUnits = workerUnits[0];
    }

    setUnitsOnReview([firstWrokerUnits[0], [...firstWrokerUnits[1]]]);
    setCurrentWorkerOnReview(firstWrokerUnits[0]);
    setModalData({...modalData, applyToNextUnitsCount: [...firstWrokerUnits[1]].length});

    const firstUnit = firstWrokerUnits[1].shift();
    setCurrentUnitOnReview(firstUnit);
  };

  const onReviewSuccess = (_modalData: ModalDataType, unitIds: number[]) => {
    if (_modalData.type === ReviewType.APPROVE) {
      // Grant Qualification
      if (_modalData.form.checkboxAssignQualification && _modalData.form.qualification) {
        postQualificationGrantWorker(
          _modalData.form.qualification,
          currentWorkerOnReview,
          () => null,
          setLoading,
          onError,
          {
            feedback: _modalData.form.checkboxComment ? _modalData.form.comment : null,
            tips: _modalData.form.checkboxGiveTips ? _modalData.form.tips : null,
            unit_ids: unitIds,
            value: _modalData.form.qualificationValue,
          },
        )
      }
    }
    else if (_modalData.type === ReviewType.SOFT_REJECT) {
      // Revoke Qualification
      if (_modalData.form.checkboxAssignQualification && _modalData.form.qualification) {
        postQualificationRevokeWorker(
          _modalData.form.qualification,
          currentWorkerOnReview,
          () => null,
          setLoading,
          onError,
          {
            feedback: _modalData.form.checkboxComment ? _modalData.form.comment : null,
            unit_ids: unitIds,
            value: _modalData.form.qualificationValue,
          },
        )
      }
    }
    else if (_modalData.type === ReviewType.REJECT) {
      // Revoke Qualification
      if (_modalData.form.checkboxUnassignQualification && _modalData.form.qualification) {
        postQualificationRevokeWorker(
          _modalData.form.qualification,
          currentWorkerOnReview,
          () => null,
          setLoading,
          onError,
          {
            feedback: _modalData.form.checkboxComment ? _modalData.form.comment : null,
            unit_ids: unitIds,
          },
        )
      }
      // Block Worker
      if (_modalData.form.checkboxBanWorker) {
        postWorkerBlock(
          currentWorkerOnReview,
          () => null,
          setLoading,
          onError,
          {
            feedback: _modalData.form.checkboxComment ? _modalData.form.comment : null,
            unit_ids: unitIds,
          },
        )
      }
    }

    // Try to get next Unit
    setNextUnit();
  };

  const getUnitsIdsByApplyToNext = (applyToNext: boolean): number[] => {
    let unitIds = [currentUnitOnReview];

    if (applyToNext) {
      unitIds = [...unitIds, ...workerUnits.shift()[1]];
    }

    return unitIds;
  };

  const onModalSubmit = () => {
    setModalShow(false);

    const unitIds = getUnitsIdsByApplyToNext(modalData.applyToNext);

    if (modalData.type === ReviewType.APPROVE) {
      postUnitsApprove(
        () => onReviewSuccess(modalData, unitIds), setLoading, onError, {unit_ids: unitIds},
      );
    }
    else if (modalData.type === ReviewType.SOFT_REJECT) {
      postUnitsSoftReject(
        () => onReviewSuccess(modalData, unitIds), setLoading, onError, {unit_ids: unitIds},
      );
    }
    else if (modalData.type === ReviewType.REJECT) {
      postUnitsReject(
        () => onReviewSuccess(modalData, unitIds), setLoading, onError, {unit_ids: unitIds},
      );
    }

    // Save current state of the modal data
    updateModalState(setModalState, modalData.type, modalData);
  };

  const onError = (errorResponse: ErrorResponseType | null) => {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  };

  // [RECEIVING WIDGET DATA]
  // ---
  const sendDataToTaskIframe = (data: object) => {
    const reviewData = {
      REVIEW_DATA: data,
    }
    const taskIframe =  iframeRef.current;
    taskIframe.contentWindow.postMessage(JSON.stringify(reviewData), '*');
  };
  // ---

  const currentUnitDetails = unitDetailsMap[String(currentUnitOnReview)];

  // Effects
  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Review - Task");
    setFinishedTask(false);

    if (task === null) {
      getTask(Number(params.id), setTask, setLoading, onError, null);
    }

    if (units === null) {
      getTaskWorkerUnitsIds(
        Number(params.id), onGetTaskWorkerUnitsIdsSuccess, setLoading, onError,
      );
    }
  }, []);

  useEffect(() => {
    if (task) {
      // Update title with current task
      setPageTitle(`Mephisto - Task Review - ${task.name}`);
    }
  }, [task]);

  useEffect(() => {
    if (workerUnits && Object.keys(workerUnits).length) {
      setNextUnit();
    }

    // Redirect back to the tasks page if there's no units to review
    if (workerUnits && Object.keys(workerUnits).length === 0) {
      navigate(urls.client.tasks);
    }
  }, [workerUnits]);

  useEffect(() => {
    if (unitsOnReview && unitsOnReview[1].length) {
      getUnits(
        setUnits, setLoading, onError, {task_id: params.id, unit_ids: unitsOnReview[1].join(',')},
      );
    }
  }, [unitsOnReview]);

  useEffect(() => {
    if (units && currentUnitOnReview) {
      setUnitDetailsMap(() => {
        const map = {};
        units.forEach((item: UnitType) => {
          map[item.id] = item;
        });
        return map;
      });

      getStats(setTaskStats, setLoading, onError, {task_id: params.id});
      getStats(
        setWorkerStats,
        setLoading,
        onError,
        {task_id: params.id, worker_id: currentWorkerOnReview},
      );
      getUnitsDetails(setUnitDetails, setLoading, onError, {unit_ids: currentUnitOnReview});
    }
  }, [units, currentUnitOnReview]);

  useEffect(() => {
    if (finishedTask === true) {
      getStats(setTaskStats, setLoading, onError, {task_id: params.id});
      getStats(
        setWorkerStats,
        setLoading,
        onError,
        {task_id: params.id, worker_id: currentWorkerOnReview},
      );

      setTimeout(() => {
        navigate(urls.client.tasks);
      }, 5000);
    }
  }, [finishedTask]);

  useEffect(() => {
    if (unitDetails) {
      setUnitDetailsMap((oldValue: UnitDetailsMapType) => {
        const map = cloneDeep(oldValue);
        unitDetails.forEach((item: UnitDetailsType) => {
          const prev = map[item.id];
          map[item.id] = {...prev, ...item};
        });
        return map;
      });
    }
  }, [unitDetails]);

  // [RECEIVING WIDGET DATA]
  // ---
  useEffect(() => {
    if (
      iframeLoaded &&
      currentUnitDetails?.outputs &&
      'final_submission' in currentUnitDetails.outputs
    ) {
      sendDataToTaskIframe(currentUnitDetails.outputs);
    }
  }, [currentUnitDetails, iframeLoaded]);
  // ---

  if (task === null) {
    return null;
  }

  return <div className={'task'}>
    <TaskHeader
      taskStats={taskStats}
      workerStats={workerStats}
      workerId={unitsOnReview ? currentWorkerOnReview : null}
    />

    <div className={"buttons"}>
      {!finishedTask ? (<>
        <Button variant={"success"} size={"sm"} onClick={onApproveClick}>Approve</Button>
        <Button variant={"warning"} size={"sm"} onClick={onSoftRejectClick}>Soft-Reject</Button>
        <Button variant={"danger"} size={"sm"} onClick={onRejectClick}>Reject</Button>
      </>) : (
        <div>No units left for this task. Redirecting to the list of tasks.</div>
      )}
    </div>

    <div className={"content"}>
      {/* Preloader when we request tasks */}
      {loading && (
        <div className={"loading"}>
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      )}

      {/* Unit info */}
      {unitDetails && currentUnitOnReview && (
        <div className={"info"}>
          {currentUnitDetails && (<>
            <div>Unit ID: {currentUnitDetails.id}</div>
            <div>Task ID: {currentUnitDetails.task_id}</div>
            <div>Worker ID: {currentUnitDetails.worker_id}</div>
          </>)}
        </div>
      )}

      {currentUnitDetails?.outputs && (<>
        {/* Task info */}
        <div className={'question'} onClick={(e) => e.preventDefault()}>
          {'final_submission' in currentUnitDetails.outputs ? (<>
            {/* TODO [RECEIVING WIDGET DATA]: Remove this later if `iframe` is OK */}
            {/*<div className={'images'}>*/}
            {/*  {(currentUnitDetails.outputs['final_submission']['annotations'] || []).map(*/}
            {/*    (item: {[key: string]: any}, i: number) => {*/}
            {/*      return <img src={item['imgData']} key={'img' + i} alt={'img' + i} />;*/}
            {/*    }*/}
            {/*  )}*/}
            {/*</div>*/}
            {/*<TaskFrontend*/}
            {/*  classifyDigit={(_) => null}*/}
            {/*  handleSubmit={(e) => console.log('handleSubmit', e)}*/}
            {/*  taskData={currentUnitDetails.outputs['init_data'] || {isScreeningUnit: false}}*/}
            {/*/>*/}

            {/* [RECEIVING WIDGET DATA] */}
            {/* --- */}
            {/*
              NOTE: We need to pass `review_mode=true` to tell MNIST app
                    not to show default view and make any requests to server
            */}
            <iframe
              src={`${MNIST_URL}/?review_mode=true`}
              id={'task-preview'}
              width={1000}
              height={610}
              onLoad={() => setIframeLoaded(true)}
              ref={iframeRef}
            />
            {/* --- */}
          </>) : (
            <JSONPretty className={"json-pretty"} data={currentUnitDetails.inputs} space={4} />
          )}
        </div>

        {/* Results table */}
        <div className={"results"}>
          <h1><b>Results:</b></h1>

          {'final_submission' in currentUnitDetails.outputs ? (
            <Table className={"results-table"} responsive={"sm"} bordered={false}>
              <thead>
                <tr className={"titles-row"}>
                  <th className={"title"}><b>Predicted Number</b></th>
                  <th className={"title"}><b>Annotation Correct?</b></th>
                  <th className={"title"}><b>Corrected Annotation</b></th>
                </tr>
              </thead>
              <tbody>
                {(currentUnitDetails.outputs['final_submission']['annotations'] || []).map(
                  (item: {[key: string]: any}, i: number) => {
                    return <tr className={"results-row"} key={"results-row" + i}>
                      <td className={"current-annotation"}>
                        <b>{item["currentAnnotation"]}</b>
                      </td>
                      <td className={"is-correct"}>
                        <b>{item["isCorrect"] ? 'Yes': 'No'}</b>
                      </td>
                      <td>
                        <b>{item["trueAnnotation"]}</b>
                      </td>
                    </tr>;
                  }
                )}
              </tbody>
            </Table>
          ) : (
            <JSONPretty className={"json-pretty"} data={currentUnitDetails.outputs} space={4} />
          )}
        </div>
      </>)}
    </div>

    <ReviewModal
      show={modalShow}
      setShow={setModalShow}
      data={modalData}
      setData={setModalData}
      onSubmit={onModalSubmit}
      setErrors={props.setErrors}
      workerId={currentWorkerOnReview}
    />
  </div>;
}


export default TaskPage;
