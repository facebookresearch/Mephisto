/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import EditGrantedQualificationModal from "components/EditGrantedQualificationModal/EditGrantedQualificationModal";
import Preloader from "components/Preloader/Preloader";
import { setResponseErrors } from "helpers";
import * as React from "react";
import { useEffect } from "react";
import { Button } from "react-bootstrap";
import {
  getGrantedQualifications,
  getQualifications,
  patchQualificationGrantWorker,
  patchQualificationRevokeWorker,
  postQualification,
} from "requests/qualifications";
import CreateQualificationModal from "../CreateQualificationModal/CreateQualificationModal";
import QualificationsTable from "../QualificationsTable/QualificationsTable";
import "./QualificationsTab.css";

interface QualificationsTabPropsType {
  setErrors: Function;
}

function QualificationsTab(props: QualificationsTabPropsType) {
  const [grantedQualifications, setGrantedQualifications] = React.useState<
    FullGrantedQualificationType[]
  >(null);
  const [selectedQualification, setSelectedQualification] = React.useState<
    string
  >(null);
  const [qualifications, setQualifications] = React.useState<
    QualificationType[]
  >([]);
  const [loading, setLoading] = React.useState(false);
  const [createModalShow, setCreateModalShow] = React.useState<boolean>(false);
  const [editModalShow, setEditModalShow] = React.useState<boolean>(false);
  const [
    editModalGrantedQualification,
    setEditModalGrantedQualification,
  ] = React.useState<FullGrantedQualificationType>(null);

  const hasGrantedQualifications =
    grantedQualifications && grantedQualifications.length !== 0;

  // Methods

  const onError = (response: ErrorResponseType) =>
    setResponseErrors(props.setErrors, response);

  function requestQualifications() {
    getQualifications(setQualifications, setLoading, onError);
  }

  function requestGrantedQualifications(
    getParams: { [key: string]: string | number } = null
  ) {
    getGrantedQualifications(
      setGrantedQualifications,
      setLoading,
      onError,
      getParams
    );
  }

  function onCreateModalSubmit(data: CreateQualificationFormType) {
    function onSuccess() {
      requestQualifications();
      setCreateModalShow(false);
    }

    postQualification(onSuccess, () => null, onError, data);
  }

  function onEditModalSubmit(
    qualificationId: string,
    workerId: string,
    value: number
  ) {
    function onSuccess() {
      requestGrantedQualifications();
      setEditModalShow(false);
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

  function onEditModalRevoke(qualificationId: string, workerId: string) {
    function onSuccess() {
      requestGrantedQualifications();
      setEditModalShow(false);
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
    document.title = "Mephisto - Task Review - All Qualifications";

    if (qualifications.length === 0) {
      requestQualifications();
    }

    if (grantedQualifications === null) {
      requestGrantedQualifications();
    }
  }, []);

  useEffect(() => {
    const getParams = {};
    if (![null, ""].includes(selectedQualification)) {
      getParams["qualification_id"] = selectedQualification;
    }

    requestGrantedQualifications(getParams);
  }, [selectedQualification]);

  return (
    <div className={`qualifications-tab`}>
      <div className={`qualification-actions`}>
        <div className={`filter-qualifications`}>
          <label className={`select-qualifications-label`}>
            Filter by qualification
          </label>

          <select
            className={`
              form-select
              form-select-sm
              select-qualifications
            `}
            onChange={(e) => setSelectedQualification(e.target.value)}
          >
            <option value={""} selected>
              All qualifications
            </option>
            {qualifications.map((q: QualificationType) => {
              return (
                <option key={`qual-${q.id}`} value={q.id}>
                  {q.name}
                </option>
              );
            })}
          </select>
        </div>

        <div className={`buttons`}>
          <Button
            variant={"primary"}
            size={"sm"}
            onClick={() => setCreateModalShow(true)}
          >
            Create qualification
          </Button>
        </div>
      </div>

      {hasGrantedQualifications ? (
        <QualificationsTable
          grantedQualifications={grantedQualifications}
          setEditModalGrantedQualification={setEditModalGrantedQualification}
          setEditModalShow={setEditModalShow}
          setErrors={props.setErrors}
        />
      ) : (
        <div className={`empty-message`}>
          This qualification has not been granted to any worker yet.
        </div>
      )}

      <Preloader loading={loading} />

      <CreateQualificationModal
        show={createModalShow}
        setShow={setCreateModalShow}
        onSubmit={onCreateModalSubmit}
        setErrors={props.setErrors}
      />

      <EditGrantedQualificationModal
        grantedQualification={editModalGrantedQualification}
        onRevoke={onEditModalRevoke}
        onSubmit={onEditModalSubmit}
        setErrors={props.setErrors}
        setShow={setEditModalShow}
        show={editModalShow}
      />
    </div>
  );
}

export default QualificationsTab;
