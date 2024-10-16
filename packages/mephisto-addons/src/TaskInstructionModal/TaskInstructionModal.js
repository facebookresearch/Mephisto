/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import "./TaskInstructionModal.css";

export default function TaskInstructionModal({
  className,
  classNameDialog,
  instructions,
  open,
  setOpen,
  title,
}) {
  const modalContentRef = React.useRef(null);

  const [modalContentTopPosition, setModalContentTopPosition] = React.useState(
    0
  );

  function onScrollModalContent(e) {
    // Save scrolling position to restore it when we open this modal again
    setModalContentTopPosition(e.currentTarget.scrollTop);
  }

  React.useEffect(() => {
    if (open) {
      // Set saved scrolling position to continue reading from that place we stopped.
      // This is needed in case if instruction is too long,
      // and it is hard to start searching previous place again
      modalContentRef.current.scrollTo(0, modalContentTopPosition);
    }
  }, [open]);

  return (
    // bootstrap classes:
    //  - modal
    //  - modal-dialog
    //  - modal-dialog-scrollable
    //  - modal-content
    //  - modal-header
    //  - modal-title
    //  - close
    //  - modal-body

    <div
      className={`task-instruction-modal modal ${className || ""}`}
      id={"id-task-instruction-modal"}
      data-backdrop={"static"}
      data-keyboard={"false"}
      tabIndex={"-1"}
      aria-labelledby={"id-modal-title"}
      aria-hidden={"true"}
    >
      <div
        className={`
          modal-dialog
          modal-dialog-scrollable
          ${classNameDialog || ""}
        `}
      >
        <div className={"modal-content"}>
          <div className={"modal-header"}>
            <div className={"modal-title"} id={"id-modal-title"}>
              {title}
            </div>

            <button
              type={"button"}
              className={"close"}
              data-dismiss={"modal"}
              aria-label={"Close"}
              onClick={() => setOpen(false)}
            >
              <span aria-hidden={"true"}>&times;</span>
            </button>
          </div>

          <div
            className={"modal-body"}
            onScroll={onScrollModalContent}
            ref={modalContentRef}
          >
            {instructions}
          </div>
        </div>
      </div>
    </div>
  );
}
