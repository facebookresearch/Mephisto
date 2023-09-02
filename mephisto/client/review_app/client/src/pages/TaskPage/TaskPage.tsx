/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import cloneDeep from 'lodash/cloneDeep';
import * as React from 'react';
import { useEffect } from 'react';
import { Button } from 'react-bootstrap';
import { useParams } from 'react-router-dom';
import { getUnits } from 'requests/units';
import Header from './Header/Header';
import {
  APPROVE_MODAL_DATA_STATE,
  REJECT_MODAL_DATA_STATE,
  SOFT_REJECT_MODAL_DATA_STATE,
} from './modalData';
import ReviewModal from './ReviewModal/ReviewModal';
import './TaskPage.css';


type ParamsType = {
  id: string;
};


function TaskPage() {
  const params = useParams<ParamsType>();

  const [units, setUnits] = React.useState<Array<Unit>>(null);
  const [loading, setLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<ErrorResponse>(null);

  const [modalShow, setModalShow] = React.useState<boolean>(false);
  const [modalData, setModalData] = React.useState<ModalDataType>(
    cloneDeep(APPROVE_MODAL_DATA_STATE)
  );

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

  const onModalSubmit = () => {
    setModalShow(false);
    console.log('Data:', modalData);
  };

  // Effects
  useEffect(() => {
    if (units === null) {
      getUnits(setUnits, setLoading, setErrors, {task_id: params.id});
    }
  }, []);

  if (units === null) {
    return null;
  }

  return <div className={'task'}>
    <Header />

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
