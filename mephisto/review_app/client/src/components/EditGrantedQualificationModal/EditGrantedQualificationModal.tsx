/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  EDIT_GRANTED_QUALIFICATION_EXPLANATION_LENGTH,
  EDIT_GRANTED_QUALIFICATION_VALUE_LENGTH,
} from "consts/review";
import cloneDeep from "lodash/cloneDeep";
import * as React from "react";
import { useEffect } from "react";
import { Button, Col, Form, Modal, Row } from "react-bootstrap";
import "./EditGrantedQualificationModal.css";

export type EditGrantedQualificationFormType = {
  value: number;
  explanation?: string;
};

type EditGrantedQualificationModalPropsType = {
  grantedQualification: FullGrantedQualificationType;
  onRevoke: Function;
  onSubmit: Function;
  setErrors: Function;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
  show: boolean;
};

function EditGrantedQualificationModal(
  props: EditGrantedQualificationModalPropsType
) {
  const defaultFormValue = {
    value: props.grantedQualification?.value_current || 0,
  };

  const [form, setForm] = React.useState<EditGrantedQualificationFormType>(
    cloneDeep(defaultFormValue)
  );
  const [formIsValid, setFormIsValid] = React.useState<boolean>(false);
  const [valueHasChanged, setValueHasChanged] = React.useState<boolean>(false);

  const revokeButtonDisabled = valueHasChanged;
  const saveButtonDisabled = !valueHasChanged || !formIsValid;

  // Methods

  function onModalClose() {
    props.setShow(!props.show);
  }

  function updateForm(fieldName: string, value: string) {
    if (fieldName === "value") {
      const re = /^[0-9\b]+$/;
      // if value is not blank, then test the regex
      if (value === "" || re.test(value)) {
        setForm({ ...form, [fieldName]: parseInt(value) });
      }
      setValueHasChanged(true);
    } else {
      setForm({ ...form, [fieldName]: value });
    }
  }

  // Effects

  useEffect(() => {
    if (String(form.value) !== "") {
      setFormIsValid(true);
    } else {
      setFormIsValid(false);
    }
  }, [form]);

  useEffect(() => {
    if (props.show) {
      setForm(cloneDeep(defaultFormValue));
      setValueHasChanged(false);
    }
  }, [props.show]);

  return (
    props.show && (
      <Modal
        className={"edit-granted-qualification-modal"}
        show={props.show}
        onHide={onModalClose}
      >
        <Modal.Header closeButton={true}>
          <Modal.Title>Edit Worker Qualification</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <Form
            className={"edit-granted-qualification-form"}
            method={"POST"}
            onSubmit={(e) => {
              e.preventDefault();
            }}
          >
            <Form.Group as={Row} className={`mb-2`} controlId={"name"}>
              <Form.Label>
                <small>Qualification value</small>
              </Form.Label>

              <Col>
                <Form.Control
                  size={"sm"}
                  type={"input"}
                  placeholder={"Value"}
                  value={form.value || ""}
                  maxLength={EDIT_GRANTED_QUALIFICATION_VALUE_LENGTH}
                  onChange={(e) => updateForm("value", e.target.value)}
                />
              </Col>
            </Form.Group>

            <Form.Group as={Row} className={`mb-2`} controlId={"name"}>
              <Form.Label>
                <small>Explanation</small>
              </Form.Label>

              <Col>
                <Form.Control
                  size={"sm"}
                  type={"textarea"}
                  placeholder={"Explanation"}
                  value={form.explanation || ""}
                  as={"textarea"}
                  rows={3}
                  maxLength={EDIT_GRANTED_QUALIFICATION_EXPLANATION_LENGTH}
                  onChange={(e) => updateForm("explanation", e.target.value)}
                />
              </Col>
            </Form.Group>
          </Form>
        </Modal.Body>

        <Modal.Footer>
          <div className={"edit-granted-qualification-buttons"}>
            <Button
              variant={"outline-secondary"}
              size={"sm"}
              onClick={onModalClose}
            >
              Cancel
            </Button>

            <div className={`right-buttons`}>
              <Button
                type={"button"}
                variant={"danger"}
                size={"sm"}
                disabled={revokeButtonDisabled}
                onClick={() => {
                  props.onRevoke(
                    props.grantedQualification.qualification_id,
                    props.grantedQualification.worker_id
                  );
                }}
              >
                Revoke qualification
              </Button>

              <Button
                variant={"success"}
                size={"sm"}
                disabled={saveButtonDisabled}
                onClick={() => {
                  if (formIsValid) {
                    props.onSubmit(
                      props.grantedQualification.qualification_id,
                      props.grantedQualification.worker_id,
                      form
                    );
                  }
                }}
              >
                Save
              </Button>
            </div>
          </div>
        </Modal.Footer>
      </Modal>
    )
  );
}

export default EditGrantedQualificationModal;
