/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Header from 'components/Header/Header';
// TODO: Find the way to import it dynamically
import { TaskFrontend } from 'components/mnist_core_components_copied';
import { ReviewType } from 'consts/review';
import cloneDeep from 'lodash/cloneDeep';
import * as React from 'react';
import { useEffect } from 'react';
import { Button, Table } from 'react-bootstrap';
import { useParams } from 'react-router-dom';
import { getStats } from 'requests/stats';
import { getTask, getTaskWorkerUnitsIds } from 'requests/tasks';
import {
  getUnits,
  getUnitsDetails,
  postUnitsApprove,
  postUnitsReject,
  postUnitsSoftReject,
} from 'requests/units';
import { setPageTitle, updateModalState } from './helpers';
import {
  APPROVE_MODAL_DATA_STATE,
  DEFAULT_MODAL_STATE_VALUE,
  REJECT_MODAL_DATA_STATE,
  SOFT_REJECT_MODAL_DATA_STATE,
} from './modalData';
import ReviewModal from './ReviewModal/ReviewModal';
import './TaskPage.css';


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


function TaskPage() {
  const params = useParams<ParamsType>();

  const [task, setTask] = React.useState<TaskType>(null);
  const [units, setUnits] = React.useState<Array<UnitType>>(null);
  const [loading, setLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<ErrorResponseType>(null);

  const [modalShow, setModalShow] = React.useState<boolean>(false);
  const [modalData, setModalData] = React.useState<ModalDataType>(
    cloneDeep(APPROVE_MODAL_DATA_STATE)
  );

  const [modalState, setModalState] = React.useState<ModalStateType>(
    cloneDeep(DEFAULT_MODAL_STATE_VALUE)
  );

  const [taskStats, setTaskStats] = React.useState<TaskStatsType>(defaultStats);
  const [workerStats, setWorkerStats] = React.useState<WorkerStatsType>(defaultStats);
  const [workerUnits, setWorkerUnits] = React.useState<Array<[number, number[]]>>([]);
  const [unitsOnReview, setUnitsOnReview] = React.useState<[number, number[]]>(null);
  const [currentWorkerOnReview, setcurrentWorkerOnReview] = React.useState<number>(null);
  const [currentUnitOnReview, setCurrentUnitOnReview] = React.useState<number>(null);
  const [unitDetails, setUnitDetails] = React.useState<UnitDetailsType[]>(null);
  const [unitDetailsMap, setUnitDetailsMap] = React.useState<UnitDetailsMapType>({});

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
    const defaultValue = cloneDeep(APPROVE_MODAL_DATA_STATE);
    defaultValue.applyToNext = modalState.approve.applyToNext;

    if (defaultValue.applyToNext) {
      defaultValue.form = modalState.approve.form;
    }

    setModalShow(true);
    setModalData(defaultValue);
  };

  const onSoftRejectClick = () => {
    const defaultValue = cloneDeep(SOFT_REJECT_MODAL_DATA_STATE);
    defaultValue.applyToNext = modalState.softReject.applyToNext;

    if (defaultValue.applyToNext) {
      defaultValue.form = modalState.softReject.form;
    }

    setModalShow(true);
    setModalData(defaultValue);
  };

  const onRejectClick = () => {
    const defaultValue = cloneDeep(REJECT_MODAL_DATA_STATE);
    defaultValue.applyToNext = modalState.reject.applyToNext;

    if (defaultValue.applyToNext) {
      defaultValue.form = modalState.reject.form;
    }

    setModalShow(true);
    setModalData(defaultValue);
  };

  const onModalSubmitSuccess = () => {

  };

  const onModalSubmit = () => {
    setModalShow(false);
    console.log('Data:', modalData);

    if (modalData.type === ReviewType.APPROVE) {
      postUnitsApprove(
        onModalSubmitSuccess, setLoading, setErrors, {unit_ids: [currentUnitOnReview]},
      );
    }
    else if (modalData.type === ReviewType.SOFT_REJECT) {
      postUnitsSoftReject(
        onModalSubmitSuccess, setLoading, setErrors, {unit_ids: [currentUnitOnReview]},
      );
    }
    else if (modalData.type === ReviewType.REJECT) {
      postUnitsReject(
        onModalSubmitSuccess, setLoading, setErrors, {unit_ids: [currentUnitOnReview]},
      );
    }

    // Save current state of the modal data
    updateModalState(setModalState, modalData.type, modalData);
  };

  // Effects
  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Review - Task");

    if (task === null) {
      getTask(Number(params.id), setTask, setLoading, setErrors, null);
    }

    if (units === null) {
      getTaskWorkerUnitsIds(
        Number(params.id), onGetTaskWorkerUnitsIdsSuccess, setLoading, setErrors,
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
    if (Object.keys(workerUnits).length) {
      const firstWrokerUnits = workerUnits[0];
      setUnitsOnReview(firstWrokerUnits);
      setcurrentWorkerOnReview(firstWrokerUnits[0]);
      setCurrentUnitOnReview(firstWrokerUnits[1][0]);
    }
  }, [workerUnits]);

  useEffect(() => {
    if (unitsOnReview && unitsOnReview[1].length) {
      getUnits(
        setUnits, setLoading, setErrors, {task_id: params.id, unit_ids: unitsOnReview[1].join(',')},
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

      getStats(setTaskStats, setLoading, setErrors, {task_id: params.id});
      getStats(setWorkerStats, setLoading, setErrors, {worker_id: currentWorkerOnReview});
      getUnitsDetails(setUnitDetails, setLoading, setErrors, {unit_ids: currentUnitOnReview});
    }
  }, [units, currentUnitOnReview]);

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

  if (units === null) {
    return null;
  }

  const currentUnitDetails = unitDetailsMap[String(currentUnitOnReview)];

  return <div className={'task'}>
    <Header
      taskStats={taskStats}
      workerStats={workerStats}
      workerId={unitsOnReview ? currentWorkerOnReview : null}
    />

    <div className={"buttons"}>
      <Button variant={"success"} size={"sm"} onClick={onApproveClick}>Approve</Button>
      <Button variant={"warning"} size={"sm"} onClick={onSoftRejectClick}>Soft-Reject</Button>
      <Button variant={"danger"} size={"sm"} onClick={onRejectClick}>Reject</Button>
    </div>

    <div className={"content"}>
      {/* Unit info */}
      {unitDetails && currentUnitOnReview && (
        <div className={"info"}>
          {currentUnitDetails && (<>
            <div>Unit ID: {currentUnitDetails.id}</div>
            <div>Task ID: {currentUnitDetails.task_id}</div>
            <div>Worker ID: {currentUnitDetails.worker_id}</div>
            <div>Status: {currentUnitDetails.status}</div>
          </>)}
        </div>
      )}

      {currentUnitDetails?.data && (<>
        {/* Task info */}
        <div className={'question'} onClick={(e) => e.preventDefault()}>
          <h1><b>Task:</b></h1>
          {currentUnitDetails.inputs ? (
            <div>{JSON.stringify(currentUnitDetails.inputs)}</div>
          ) : (<>
             <div className={'images'}>
              {(currentUnitDetails.data['final_submission']['annotations'] || []).map(
                (item: {[key: string]: any}, i: number) => {
                  return <img src={item['imgData']} key={'img' + i} alt={'img' + i} />;
                }
              )}
            </div>
            <TaskFrontend
              classifyDigit={(_) => null}
              handleSubmit={(e) => console.log('handleSubmit', e)}
              taskData={currentUnitDetails.data['init_data']}
            />
          </>)}

        </div>

        {/* Results table */}
        <div className={"results"}>
          <h1><b>Results:</b></h1>

          {currentUnitDetails.outputs ? (
            <div>{JSON.stringify(currentUnitDetails.outputs)}</div>
          ) : (
            <Table className={"results-table"} responsive={"sm"} bordered={false}>
              <thead>
                <tr className={"titles-row"}>
                  <th className={"title"}><b>Predicted Number</b></th>
                  <th className={"title"}><b>Annotation Correct?</b></th>
                  <th className={"title"}><b>Corrected Annotation</b></th>
                </tr>
              </thead>
              <tbody>
                {(currentUnitDetails.data['final_submission']['annotations'] || []).map(
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
    />
  </div>;
}


export default TaskPage;
