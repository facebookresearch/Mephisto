/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import EditGrantedQualificationModal, {
  EditGrantedQualificationFormType,
} from "components/EditGrantedQualificationModal/EditGrantedQualificationModal";
import Preloader from "components/Preloader/Preloader";
import { setResponseErrors } from "helpers";
import cloneDeep from "lodash/cloneDeep";
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

const DEFAUTL_GRANTED_QUALIFICATIONS_PARAMS = {};

type GrantedQualificationsParamsType = {
  qualification_id?: string;
  sort?: string;
};

type QualificationsTabPropsType = {
  setErrors: Function;
};

function QualificationsTab(props: QualificationsTabPropsType) {
  const [grantedQualifications, setGrantedQualifications] = React.useState<
    FullGrantedQualificationType[]
  >(null);
  const [
    grantedQualificationsParams,
    setGrantedQualificationsParams,
  ] = React.useState<GrantedQualificationsParamsType>(
    DEFAUTL_GRANTED_QUALIFICATIONS_PARAMS
  );
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

  function requestGrantedQualifications() {
    getGrantedQualifications(
      setGrantedQualifications,
      setLoading,
      onError,
      grantedQualificationsParams
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
    data: EditGrantedQualificationFormType
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
      data
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

  function onSelectQualification(qualificationId: string) {
    setGrantedQualificationsParams(
      (oldValue: GrantedQualificationsParamsType) => {
        const newValue = cloneDeep(oldValue);
        if (qualificationId) {
          newValue.qualification_id = qualificationId;
        } else {
          delete newValue.qualification_id;
        }
        return newValue;
      }
    );
  }

  function onChangeTableSortParam(param: string) {
    setGrantedQualificationsParams(
      (oldValue: GrantedQualificationsParamsType) => {
        const newValue = cloneDeep(oldValue);
        if (param) {
          newValue.sort = param;
        } else {
          delete newValue.sort;
        }
        return newValue;
      }
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
    requestGrantedQualifications();
  }, [grantedQualificationsParams]);

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
            onChange={(e) => onSelectQualification(e.target.value)}
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
          onChangeSortParam={(param: string) => onChangeTableSortParam(param)}
          setEditModalGrantedQualification={setEditModalGrantedQualification}
          setEditModalShow={setEditModalShow}
          setErrors={props.setErrors}
        />
      ) : (
        <div className={`empty-message`}>
          No qualifications has been granted to any worker yet.
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
