/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import EditGrantedQualificationModal from "components/EditGrantedQualificationModal/EditGrantedQualificationModal";
import Preloader from "components/Preloader/Preloader";
import TasksHeader from "components/TasksHeader/TasksHeader";
import { DEFAULT_DATE_FORMAT } from "consts/format";
import { setResponseErrors } from "helpers";
import * as moment from "moment";
import * as React from "react";
import { useEffect } from "react";
import { Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import {
  deleteQualification,
  getGrantedQualifications,
  getQualification,
  getQualificationDetails,
  patchQualification,
  patchQualificationGrantWorker,
  patchQualificationRevokeWorker,
} from "requests/qualifications";
import urls from "urls";
import DeleteQualificationModal from "./DeleteQualificationModal/DeleteQualificationModal";
import EditQualificationModal from "./EditQualificationModal/EditQualificationModal";
import GrantedQualificationsTable from "./GrantedQualificationsTable/GrantedQualificationsTable";
import "./QualificationPage.css";

type ParamsType = {
  id: string;
};

type QualificationPagePropsType = {
  setErrors: Function;
};

function QualificationPage(props: QualificationPagePropsType) {
  const params = useParams<ParamsType>();

  const [qualification, setQualification] = React.useState<QualificationType>(
    null
  );
  const [grantedQualifications, setGrantedQualifications] = React.useState<
    FullGrantedQualificationType[]
  >(null);
  const [loading, setLoading] = React.useState(false);
  const [
    editQualificationModalShow,
    setEditQualificationModalShow,
  ] = React.useState<boolean>(false);
  const [
    deleteQualificationModalShow,
    setDeleteQualificationModalShow,
  ] = React.useState<boolean>(false);
  const [
    grantedQualificationsAmount,
    setGrantedQualificationsAmount,
  ] = React.useState<number>(0);
  const [
    editGrantedQualificationModalShow,
    setEditGrantedQualificationModalShow,
  ] = React.useState<boolean>(false);
  const [
    editModalGrantedQualification,
    setEditModalGrantedQualification,
  ] = React.useState<FullGrantedQualificationType>(null);

  const onError = (response: ErrorResponseType) =>
    setResponseErrors(props.setErrors, response);

  // Methods

  function requestQualification() {
    getQualification(params.id, setQualification, setLoading, onError);
  }

  function requestGrantedQualifications() {
    getGrantedQualifications(setGrantedQualifications, setLoading, onError, {
      qualification_id: qualification?.id,
    });
  }

  function onClickDeleteButton() {
    function onSuccess(amount: number) {
      setGrantedQualificationsAmount(amount);
      setDeleteQualificationModalShow(true);
    }

    getQualificationDetails(
      qualification.id,
      (data: QualificationDetailsType) =>
        onSuccess(data.granted_qualifications_count),
      () => null,
      onError
    );
  }

  function onEditQualificationModalSubmit(data: CreateQualificationFormType) {
    function onSuccess() {
      requestQualification();
      setEditQualificationModalShow(false);
    }

    patchQualification(qualification.id, onSuccess, setLoading, onError, data);
  }

  function onDeleteModalSubmit() {
    function onSuccess() {
      setDeleteQualificationModalShow(false);
      // Redirect to Tasks page
      window.location.replace(urls.client.tasks);
    }

    deleteQualification(qualification.id, onSuccess, setLoading, onError);
  }

  function onEditGrantedQualificationModalSubmit(
    qualificationId: string,
    workerId: string,
    value: number
  ) {
    function onSuccess() {
      requestGrantedQualifications();
      setEditGrantedQualificationModalShow(false);
    }

    patchQualificationGrantWorker(
      qualificationId,
      workerId,
      onSuccess,
      setLoading,
      onError,
      {
        value: value,
      }
    );
  }

  function onEditGrantedQualificationModalRevoke(
    qualificationId: string,
    workerId: string
  ) {
    function onSuccess() {
      requestGrantedQualifications();
      setEditGrantedQualificationModalShow(false);
    }

    patchQualificationRevokeWorker(
      qualificationId,
      workerId,
      onSuccess,
      setLoading,
      onError,
      null
    );
  }

  // Effects
  useEffect(() => {
    if (qualification === null) {
      requestQualification();
    }
  }, []);

  useEffect(() => {
    if (qualification === null) {
      return;
    }

    if (grantedQualifications === null) {
      requestGrantedQualifications();
    }

    document.title = `Mephisto - Task Review - Qualification "${qualification.name}"`;
  }, [qualification]);

  return (
    <div className={"qualification"}>
      <TasksHeader />

      {!loading && qualification && (
        <div className={"header"}>
          <div className={`qualification-info`}>
            <div className={"qualification-name"}>
              Qualification "{qualification.name}"
            </div>

            {qualification.description && (
              <div className={"qualification-description"}>
                {qualification.description}
              </div>
            )}

            <div className={"qualification-date"}>
              Date created:{" "}
              {moment(qualification.creation_date).format(DEFAULT_DATE_FORMAT)}
            </div>
          </div>

          <div className={`header-buttons`}>
            <Button
              variant={"primary"}
              size={"sm"}
              onClick={() => setEditQualificationModalShow(true)}
            >
              Edit qualification
            </Button>

            <Button
              variant={"danger"}
              size={"sm"}
              onClick={() => onClickDeleteButton()}
            >
              Delete qualification
            </Button>
          </div>
        </div>
      )}

      <GrantedQualificationsTable
        grantedQualifications={grantedQualifications}
        setEditModalGrantedQualification={setEditModalGrantedQualification}
        setEditModalShow={setEditGrantedQualificationModalShow}
        setErrors={props.setErrors}
      />

      <Preloader loading={loading} />

      <EditQualificationModal
        onSubmit={onEditQualificationModalSubmit}
        qualification={qualification}
        setErrors={props.setErrors}
        setShow={setEditQualificationModalShow}
        show={editQualificationModalShow}
      />

      <DeleteQualificationModal
        grantedQualificationsAmount={grantedQualificationsAmount}
        onSubmit={onDeleteModalSubmit}
        setErrors={props.setErrors}
        setShow={setDeleteQualificationModalShow}
        show={deleteQualificationModalShow}
      />

      <EditGrantedQualificationModal
        grantedQualification={editModalGrantedQualification}
        onRevoke={onEditGrantedQualificationModalRevoke}
        onSubmit={onEditGrantedQualificationModalSubmit}
        setErrors={props.setErrors}
        setShow={setEditGrantedQualificationModalShow}
        show={editGrantedQualificationModalShow}
      />
    </div>
  );
}

export default QualificationPage;
