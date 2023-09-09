/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { ReviewType } from 'consts/review';
import cloneDeep from 'lodash/cloneDeep';
import * as React from 'react';
import { useEffect } from 'react';
import { Button } from 'react-bootstrap';
import { useParams } from 'react-router-dom';
import { getStats } from 'requests/stats';
import { getTaskWorkerUnitsIds } from 'requests/tasks';
import {
  getUnits,
  getUnitsDetails,
  postUnitsApprove,
  postUnitsReject,
  postUnitsSoftReject,
} from 'requests/units';
import Header from './Header/Header';
import {
  APPROVE_MODAL_DATA_STATE,
  REJECT_MODAL_DATA_STATE,
  SOFT_REJECT_MODAL_DATA_STATE,
} from './modalData';
import ReviewModal from './ReviewModal/ReviewModal';
import './TaskPage.css';


const defaultStats = {
  total_count: 0,
  reviewed_count: 0,
  approved_count: 0,
  rejected_count: 0,
  soft_rejected_count: 0,
}


type ParamsType = {
  id: string;
};


function TaskPage() {
  const params = useParams<ParamsType>();

  const [units, setUnits] = React.useState<Array<UnitType>>(null);
  const [loading, setLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<ErrorResponseType>(null);

  const [modalShow, setModalShow] = React.useState<boolean>(false);
  const [modalData, setModalData] = React.useState<ModalDataType>(
    cloneDeep(APPROVE_MODAL_DATA_STATE)
  );

  const [taskStats, setTaskStats] = React.useState<TaskStatsType>(defaultStats);
  const [workerStats, setWorkerStats] = React.useState<WorkerStatsType>(defaultStats);
  const [workerUnits, setWorkerUnits] = React.useState<Array<[number, number[]]>>([]);
  const [unitsOnReview, setUnitsOnReview] = React.useState<[number, number[]]>(null);
  const [currentWorkerOnReview, setcurrentWorkerOnReview] = React.useState<number>(null);
  const [currentUnitOnReview, setCurrentUnitOnReview] = React.useState<number>(null);
  const [unitDetails, setUnitDetails] = React.useState<UnitDetailsType>(null);

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
    })
  };

  const onApproveClick = () => {
    setModalShow(true);
    setModalData(cloneDeep(APPROVE_MODAL_DATA_STATE));
  };

  const onSoftRejectClick = () => {
    setModalShow(true);
    setModalData(cloneDeep(SOFT_REJECT_MODAL_DATA_STATE));
  };

  const onRejectClick = () => {
    setModalShow(true);
    setModalData(cloneDeep(REJECT_MODAL_DATA_STATE));
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
  };

  // Effects
  useEffect(() => {
    if (units === null) {
      // getUnits(setUnits, setLoading, setErrors, {task_id: params.id});
      getTaskWorkerUnitsIds(
        Number(params.id), onGetTaskWorkerUnitsIdsSuccess, setLoading, setErrors,
      );
    }
  }, []);

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
      getStats(setTaskStats, setLoading, setErrors, {task_id: params.id});
      getStats(setWorkerStats, setLoading, setErrors, {worker_id: currentWorkerOnReview});
      getUnitsDetails(setUnitDetails, setLoading, setErrors, {unit_ids: currentUnitOnReview});
    }
  }, [units, currentUnitOnReview]);

  if (units === null) {
    return null;
  }

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
