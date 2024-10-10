/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from "react";
import { Button, Modal } from "react-bootstrap";
import "./DeleteQualificationModal.css";

type DeleteQualificationModalPropsType = {
  grantedQualificationsAmount: number;
  onSubmit: Function;
  setErrors: Function;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
  show: boolean;
};

function DeleteQualificationModal(props: DeleteQualificationModalPropsType) {
  // Methods

  function onModalClose() {
    props.setShow(!props.show);
  }

  return (
    props.show && (
      <Modal
        className={"delete-qualification-modal"}
        show={props.show}
        onHide={onModalClose}
      >
        <Modal.Header closeButton={true}>
          <Modal.Title>Delete qualification</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          {props.grantedQualificationsAmount === 0 ? (
            <>Are you sure you want to delete it?</>
          ) : (
            <>
              This qualification was granted {props.grantedQualificationsAmount}{" "}
              times - are you sure you want to delete it?
            </>
          )}
        </Modal.Body>

        <Modal.Footer>
          <div className={"delete-qualification-buttons"}>
            <Button
              variant={"outline-secondary"}
              size={"sm"}
              onClick={onModalClose}
            >
              Cancel
            </Button>

            <Button
              variant={"danger"}
              size={"sm"}
              onClick={() => props.onSubmit()}
            >
              Delete
            </Button>
          </div>
        </Modal.Footer>
      </Modal>
    )
  );
}

export default DeleteQualificationModal;
