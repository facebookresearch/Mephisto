/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { ReviewType } from "consts/review";
import * as React from "react";
import { Button, Form, Modal } from "react-bootstrap";
import ModalForm from "../ModalForm/ModalForm";
import "./ReviewModal.css";

const ReviewTypeButtonClassMapping = {
  [ReviewType.APPROVE]: "success",
  [ReviewType.SOFT_REJECT]: "warning",
  [ReviewType.REJECT]: "danger",
};

type ReviewModalProps = {
  data: ModalDataType;
  setData: React.Dispatch<React.SetStateAction<ModalDataType>>;
  show: boolean;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
  onSubmit: Function;
  setErrors: Function;
  workerId: number | null;
};

function ReviewModal(props: ReviewModalProps) {
  function onModalClose() {
    props.setShow(!props.show);
  }

  function onChangeApplyToNext(value: boolean) {
    props.setData({ ...props.data, applyToNext: value });
  }

  return (
    props.show && (
      <Modal className={"review-modal"} show={props.show} onHide={onModalClose}>
        <Modal.Header closeButton={false}>
          <Modal.Title>{props.data.title}</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <ModalForm
            data={props.data}
            setData={props.setData}
            setErrors={props.setErrors}
            workerId={props.workerId}
          />
        </Modal.Body>

        <Modal.Footer>
          <div className={"review-buttons"}>
            <Button
              variant={"cancel-button link"}
              size={"sm"}
              onClick={onModalClose}
            >
              <b>{props.data.buttonCancel}</b>
            </Button>
            <Button
              variant={ReviewTypeButtonClassMapping[props.data.type]}
              size={"sm"}
              onClick={() => props.onSubmit()}
            >
              {props.data.buttonSubmit}
            </Button>
          </div>
          <Form>
            {props.data.applyToNextUnitsCount > 1 && (
              <Form.Check
                className={"apply-all-checkbox"}
                type={"checkbox"}
                label={`Apply to all ${props.data.applyToNextUnitsCount} remaining worker's units`}
                id={"saveState"}
                reverse={true}
                checked={props.data.applyToNext}
                onChange={() => onChangeApplyToNext(!props.data.applyToNext)}
              />
            )}
          </Form>
        </Modal.Footer>
      </Modal>
    )
  );
}

export default ReviewModal;
