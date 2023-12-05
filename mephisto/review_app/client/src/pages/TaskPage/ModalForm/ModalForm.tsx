/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { ReviewType } from "consts/review";
import * as React from "react";
import { useEffect } from "react";
import { Button, Col, Form, Row } from "react-bootstrap";
import { getQualifications, postQualification } from "requests/qualifications";
import "./ModalForm.css";

const BONUS_FOR_WORKER_ENABLED = true;
const FEEDBACK_FOR_WORKER_ENABLED = true;

const range = (start, end) => Array.from(Array(end + 1).keys()).slice(start);

type ModalFormProps = {
  data: ModalDataType;
  setData: React.Dispatch<React.SetStateAction<ModalDataType>>;
  setErrors: Function;
  workerId: number | null;
};

function ModalForm(props: ModalFormProps) {
  const [qualifications, setQualifications] = React.useState<
    Array<QualificationType>
  >(null);
  const [
    getQualificationsloading,
    setGetQualificationsloading,
  ] = React.useState(false);
  const [_, setCreateQualificationLoading] = React.useState(false);

  const onChangeAssign = (value: boolean) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxAssignQualification = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeUnassign = (value: boolean) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxUnassignQualification = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeAssignQualification = (value: string) => {
    let prevFormData: FormType = Object(props.data.form);

    if (value === "+") {
      prevFormData.showNewQualification = true;
      prevFormData.newQualificationValue = "";
    } else {
      prevFormData.qualification = Number(value);
    }

    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeAssignQualificationValue = (value: string) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.qualificationValue = Number(value);
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeUnassignQualification = (id: string) => {
    onChangeAssignQualification(id);
  };

  const onChangeGiveBonus = (value: boolean) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxGiveBonus = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeBonus = (value: string) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.bonus = Number(value);
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeBanWorker = (value: boolean) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxBanWorker = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeWriteReviewNote = (value: boolean) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxReviewNote = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeReviewNote = (value: string) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.reviewNote = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeWriteReviewNoteSend = (value: boolean) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.checkboxReviewNoteSend = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onChangeNewQualificationValue = (value: string) => {
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.newQualificationValue = value;
    props.setData({ ...props.data, form: prevFormData });
  };

  const onClickAddNewQualification = (value: string) => {
    createNewQualification(value);
  };

  const onError = (errorResponse: ErrorResponseType | null) => {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  };

  const onCreateNewQualificationSuccess = () => {
    // Clear input
    let prevFormData: FormType = Object(props.data.form);
    prevFormData.newQualificationValue = "";
    prevFormData.showNewQualification = false;
    props.setData({ ...props.data, form: prevFormData });

    // Update select with Qualifications
    requestQualifications();
  };

  const requestQualifications = () => {
    let params;
    if (props.data.type === ReviewType.REJECT) {
      params = { worker_id: props.workerId };
    }

    getQualifications(
      setQualifications,
      setGetQualificationsloading,
      onError,
      params
    );
  };

  const createNewQualification = (name: string) => {
    postQualification(
      onCreateNewQualificationSuccess,
      setCreateQualificationLoading,
      onError,
      { name: name }
    );
  };

  // Effiects
  useEffect(() => {
    if (qualifications === null) {
      requestQualifications();
    }
  }, []);

  if (getQualificationsloading) {
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
                    <option value={""}>---</option>
                    <option value={"+"}>+ Add new qualification</option>
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
                <Col>
                  <Form.Select
                    id={"assignQualificationValue"}
                    size={"sm"}
                    value={props.data.form.qualificationValue}
                    onChange={(e) =>
                      onChangeAssignQualificationValue(e.target.value)
                    }
                  >
                    {range(1, 10).map((i) => {
                      return <option key={"qualVal" + i}>{i}</option>;
                    })}
                  </Form.Select>
                </Col>
              </Row>
              {props.data.form.showNewQualification && (
                <Row className={"third-line"}>
                  <Col xs={9}>
                    <Form.Control
                      size={"sm"}
                      type={"input"}
                      placeholder={"New qualification name"}
                      value={props.data.form.newQualificationValue || ""}
                      onChange={(e) =>
                        onChangeNewQualificationValue(e.target.value)
                      }
                    />
                  </Col>
                  <Col>
                    <Button
                      className={"new-qualification-name-button"}
                      variant={"secondary"}
                      size={"sm"}
                      onClick={() =>
                        onClickAddNewQualification(
                          props.data.form.newQualificationValue
                        )
                      }
                    >
                      Add
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
