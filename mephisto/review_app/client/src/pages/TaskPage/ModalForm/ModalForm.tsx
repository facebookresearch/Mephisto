/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  NEW_QUALIFICATION_DESCRIPTION_LENGTH,
  NEW_QUALIFICATION_NAME_LENGTH,
  ReviewType,
} from "consts/review";
import { setResponseErrors } from "helpers";
import * as React from "react";
import { useEffect } from "react";
import { Button, Col, Form, Row } from "react-bootstrap";
import { getQualifications, postQualification } from "requests/qualifications";
import { getWorkerGrantedQualifications } from "requests/workers";
import "./ModalForm.css";

const BONUS_FOR_WORKER_ENABLED = true;
const FEEDBACK_FOR_WORKER_ENABLED = true;
const QUALIFICATION_VALUE_MIN = 1;
const QUALIFICATION_VALUE_MAX = 10;

const range = (start, end) => Array.from(Array(end + 1).keys()).slice(start);

type ModalFormPropsType = {
  data: ModalDataType;
  setData: React.Dispatch<React.SetStateAction<ModalDataType>>;
  setErrors: Function;
  workerId: string | null;
};

function ModalForm(props: ModalFormPropsType) {
  const [
    workerGrantedQualifications,
    setWorkerGrantedQualifications,
  ] = React.useState<WorkerGrantedQualificationsType>({});
  const [qualifications, setQualifications] = React.useState<
    QualificationType[]
  >(null);
  const [loading, setLoading] = React.useState(false);
  const [_, setCreateQualificationLoading] = React.useState(false);
  const [
    newQualificationFormIsValid,
    setNewQualificationFormIsValid,
  ] = React.useState<boolean>(false);

  const onError = (response: ErrorResponseType) =>
    setResponseErrors(props.setErrors, response);

  // Methods
  function onChangeAssign(value: boolean) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxAssignQualification = value;
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeUnassign(value: boolean) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxUnassignQualification = value;
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeAssignQualification(value: string) {
    let prevFormData: FormType = Object(props.data.form);

    if (value === "+") {
      prevFormData.showNewQualification = true;
      prevFormData.newQualificationName = "";
      prevFormData.newQualificationDescription = "";
    } else {
      prevFormData.qualification = value;

      const prevGrantedQualification = workerGrantedQualifications[value];
      const prevGrantedQualificationValue = prevGrantedQualification?.value;
      if (prevGrantedQualificationValue !== undefined) {
        // Set to previous granted value for selected qualification
        prevFormData.qualificationValue = prevGrantedQualificationValue;
      } else {
        // Set to default value
        prevFormData.qualificationValue = QUALIFICATION_VALUE_MIN;
      }
    }

    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeAssignQualificationValue(value: string) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.qualificationValue = Number(value);
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeUnassignQualification(id: string) {
    onChangeAssignQualification(id);
  }

  function onChangeGiveBonus(value: boolean) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxGiveBonus = value;
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeBonus(value: string) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.bonus = Number(value);
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeBanWorker(value: boolean) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxBanWorker = value;

    if (props.data.type === ReviewType.REJECT) {
      if (value === true) {
        // Open review note
        prevFormData.checkboxReviewNote = true;
      } else {
        // Close review note only if there is no note typed already
        if (!prevFormData.reviewNote) {
          prevFormData.checkboxReviewNote = false;
        }
      }
    }

    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeWriteReviewNote(value: boolean) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxReviewNote = value;
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeReviewNote(value: string) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.reviewNote = value;
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeWriteReviewNoteSend(value: boolean) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxReviewNoteSend = value;
    props.setData({ ...props.data, form: prevFormData });
  }

  function onChangeNewQualificationValue(fieldName: string, value: string) {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData[fieldName] = value;
    props.setData({ ...props.data, form: prevFormData });
  }

  function onClickAddNewQualification() {
    createNewQualification(
      props.data.form.newQualificationName,
      props.data.form.newQualificationDescription
    );
  }

  function onCreateNewQualificationSuccess() {
    // Clear input
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.newQualificationName = "";
    prevFormData.newQualificationDescription = "";
    prevFormData.showNewQualification = false;
    props.setData({ ...props.data, form: prevFormData });

    // Update select with Qualifications
    requestQualifications();
  }

  function onGetWorkerGrantedQualificationsSuccess(
    grantedQualifications: GrantedQualificationType[]
  ) {
    const _workerGrantedQualifications = {};

    grantedQualifications.forEach((gq: GrantedQualificationType) => {
      _workerGrantedQualifications[gq.qualification_id] = gq;
    });
    setWorkerGrantedQualifications(_workerGrantedQualifications);
  }

  function requestQualifications() {
    let params;
    if (props.data.type === ReviewType.REJECT) {
      params = { worker_id: props.workerId };
    }

    getQualifications(setQualifications, setLoading, onError, params);
  }

  function requestWorkerGrantedQualifications() {
    getWorkerGrantedQualifications(
      props.workerId,
      onGetWorkerGrantedQualificationsSuccess,
      setLoading,
      onError
    );
  }

  function createNewQualification(name: string, description: string) {
    postQualification(
      onCreateNewQualificationSuccess,
      setCreateQualificationLoading,
      onError,
      {
        name: name,
        description: description,
      }
    );
  }

  // Effects
  useEffect(() => {
    requestWorkerGrantedQualifications();

    if (qualifications === null) {
      requestQualifications();
    }
  }, []);

  useEffect(() => {
    if (props.data.form.newQualificationName) {
      setNewQualificationFormIsValid(true);
    } else {
      setNewQualificationFormIsValid(false);
    }
  }, [props.data.form.newQualificationName]);

  if (loading) {
    return;
  }

  return (
    <Form
      className={"review-form"}
      method={"POST"}
      onSubmit={(e) => {
        e.preventDefault();
      }}
    >
      {props.data.form.checkboxAssignQualification !== undefined && (
        <>
          <Form.Check
            type={"checkbox"}
            label={"Assign Qualification"}
            id={"assign"}
            checked={props.data.form.checkboxAssignQualification}
            onChange={() =>
              onChangeAssign(!props.data.form.checkboxAssignQualification)
            }
          />

          {props.data.form.checkboxAssignQualification && (
            <>
              <Row className={"second-line"}>
                <Col xs={9}>
                  <Form.Select
                    id={"assignQualification"}
                    size={"sm"}
                    value={props.data.form.qualification || ""}
                    onChange={(e) =>
                      onChangeAssignQualification(e.target.value)
                    }
                  >
                    <optgroup>
                      <option value={""}>---</option>
                      <option value={"+"}>+ Create new qualification</option>
                    </optgroup>

                    <optgroup>
                      {qualifications &&
                        qualifications.map((q: QualificationType) => {
                          const prevGrantedQualification =
                            workerGrantedQualifications[q.id];
                          const prevGrantedQualificationValue =
                            prevGrantedQualification?.value;

                          let nameSuffix = "";
                          if (prevGrantedQualificationValue !== undefined) {
                            nameSuffix = ` (granted value: ${prevGrantedQualificationValue})`;
                          }
                          const qualificationName = `${q.name}${nameSuffix}`;

                          return (
                            <option key={`qual-${q.id}`} value={q.id}>
                              {qualificationName}
                            </option>
                          );
                        })}
                    </optgroup>
                  </Form.Select>
                </Col>
                <Col>
                  <Form.Select
                    id={"assignQualificationValue"}
                    size={"sm"}
                    value={props.data.form.qualificationValue}
                    onChange={(e) =>
                      onChangeAssignQualificationValue(e.target.value)
                    }
                  >
                    {range(
                      QUALIFICATION_VALUE_MIN,
                      QUALIFICATION_VALUE_MAX
                    ).map((i) => {
                      return <option key={"qualVal" + i}>{i}</option>;
                    })}
                  </Form.Select>
                </Col>
              </Row>
              {props.data.form.showNewQualification && (
                <Row className={"third-line"}>
                  <Col xs={9}>
                    <Form.Control
                      className={`mb-1`}
                      size={"sm"}
                      type={"input"}
                      maxLength={NEW_QUALIFICATION_NAME_LENGTH}
                      placeholder={"New qualification name"}
                      value={props.data.form.newQualificationName || ""}
                      onChange={(e) =>
                        onChangeNewQualificationValue(
                          "newQualificationName",
                          e.target.value
                        )
                      }
                    />

                    <Form.Control
                      size={"sm"}
                      type={"texarea"}
                      as={"textarea"}
                      rows={3}
                      maxLength={NEW_QUALIFICATION_DESCRIPTION_LENGTH}
                      placeholder={"Description"}
                      value={props.data.form.newQualificationDescription || ""}
                      onChange={(e) =>
                        onChangeNewQualificationValue(
                          "newQualificationDescription",
                          e.target.value
                        )
                      }
                    />
                  </Col>
                  <Col>
                    <Button
                      className={"new-qualification-name-button"}
                      variant={"secondary"}
                      size={"sm"}
                      title={
                        newQualificationFormIsValid ? "" : "Name is required"
                      }
                      disabled={!newQualificationFormIsValid}
                      onClick={() =>
                        newQualificationFormIsValid &&
                        onClickAddNewQualification()
                      }
                    >
                      Create
                    </Button>
                  </Col>
                </Row>
              )}
            </>
          )}
        </>
      )}

      {props.data.form.checkboxUnassignQualification !== undefined && (
        <>
          <Form.Check
            type={"checkbox"}
            label={"Unassign Qualification"}
            id={"unassign"}
            checked={props.data.form.checkboxUnassignQualification}
            onChange={() =>
              onChangeUnassign(!props.data.form.checkboxUnassignQualification)
            }
          />

          {props.data.form.checkboxUnassignQualification && (
            <Row className={"second-line"}>
              <Col xs={12}>
                <Form.Select
                  id={"unassignQualification"}
                  size={"sm"}
                  value={props.data.form.qualification || ""}
                  onChange={(e) =>
                    onChangeUnassignQualification(e.target.value)
                  }
                >
                  <option value={""}>---</option>
                  {qualifications &&
                    qualifications.map((q: QualificationType) => {
                      return (
                        <option key={"qual" + q.id} value={q.id}>
                          {q.name}
                        </option>
                      );
                    })}
                </Form.Select>
              </Col>
            </Row>
          )}
        </>
      )}

      <hr />

      {BONUS_FOR_WORKER_ENABLED &&
        props.data.form.checkboxGiveBonus !== undefined && (
          <>
            <Form.Check
              type={"checkbox"}
              label={"Give Bonus"}
              id={"giveBonus"}
              checked={props.data.form.checkboxGiveBonus}
              onChange={() =>
                onChangeGiveBonus(!props.data.form.checkboxGiveBonus)
              }
            />

            {props.data.form.checkboxGiveBonus && (
              <Row className={"second-line"}>
                <Col xs={4}>
                  <Form.Control
                    size={"sm"}
                    type={"input"}
                    placeholder={"Bonus"}
                    value={props.data.form.bonus || ""}
                    onChange={(e) => onChangeBonus(e.target.value)}
                  />
                </Col>
                <Col>
                  <span>Amount (cents)</span>
                </Col>
              </Row>
            )}

            <hr />
          </>
        )}

      {props.data.form.checkboxBanWorker !== undefined && (
        <>
          <Form.Check
            type={"checkbox"}
            label={"Ban Worker"}
            id={"banWorker"}
            checked={props.data.form.checkboxBanWorker}
            onChange={() =>
              onChangeBanWorker(!props.data.form.checkboxBanWorker)
            }
          />

          <hr />
        </>
      )}

      <Form.Check
        type={"checkbox"}
        label={
          FEEDBACK_FOR_WORKER_ENABLED ? "Write Note" : "Write Note for Yourself"
        }
        id={"reviewNote"}
        checked={props.data.form.checkboxReviewNote}
        onChange={() =>
          onChangeWriteReviewNote(!props.data.form.checkboxReviewNote)
        }
      />

      {props.data.form.checkboxReviewNote && (
        <>
          <Row className={"second-line"}>
            <Col>
              <Form.Control
                size={"sm"}
                as={"textarea"}
                value={props.data.form.reviewNote}
                onChange={(e) => onChangeReviewNote(e.target.value)}
              />
            </Col>
          </Row>
          {FEEDBACK_FOR_WORKER_ENABLED && (
            <Row className={"second-line"}>
              <Col>
                <Form.Check
                  type={"checkbox"}
                  label={"Share this comment with the worker"}
                  id={"reviewNoteSend"}
                  checked={props.data.form.checkboxReviewNoteSend}
                  onChange={() =>
                    onChangeWriteReviewNoteSend(
                      !props.data.form.checkboxReviewNoteSend
                    )
                  }
                />
              </Col>
            </Row>
          )}
        </>
      )}
    </Form>
  );
}

export default ModalForm;
