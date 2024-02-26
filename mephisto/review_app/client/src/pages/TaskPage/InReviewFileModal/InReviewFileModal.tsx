/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  AUDIO_TYPES_BY_EXT,
  FILE_TYPE_BY_EXT,
  FileType,
  VIDEO_TYPES_BY_EXT,
} from "consts/review";
import * as React from "react";
import { useEffect } from "react";
import { Modal } from "react-bootstrap";
import urls from "urls";
import "./InReviewFileModal.css";

type InReviewFileModalProps = {
  data: InReviewFileModalDataType;
  setData: React.Dispatch<React.SetStateAction<InReviewFileModalDataType>>;
  show: boolean;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
};

function InReviewFileModal(props: InReviewFileModalProps) {
  const { data, show, setShow } = props;

  const [fileUrl, setFileUrl] = React.useState<string>(null);
  const [fileExt, setFileExt] = React.useState<string>(null);

  const fileType = FILE_TYPE_BY_EXT[fileExt];

  function onModalClose() {
    setShow(!show);
  }

  function truncateFilename(filename: string, n: number): string {
    const ext = data.filename.split(".").pop();
    const _filename =
      filename.length > n
        ? filename.slice(0, n - 1 - ext.length) + "…" + "." + ext
        : filename;
    return _filename;
  }

  useEffect(() => {
    setFileUrl(null);
    setFileExt(null);

    if (data.filename) {
      setFileUrl(urls.server.unitsOutputsFile(data.unitId, data.filename));
      setFileExt(data.filename.split(".").pop().toLowerCase());
    }
  }, [data]);

  return (
    show && (
      <Modal
        className={"in-review-file-modal"}
        contentClassName={`file-type-${fileType}`}
        show={show}
        onHide={onModalClose}
      >
        <Modal.Header closeButton={false}>
          <button
            className={"button-close"}
            title={"Close file preview"}
            onClick={() => setShow(false)}
          >
            ✕
          </button>
          <Modal.Title>{truncateFilename(data.title, 50)}</Modal.Title>
          <a
            className={"button-download-file"}
            title={"Download file"}
            href={fileUrl}
            target={"_blank"}
          >
            ⤓
          </a>
        </Modal.Header>

        <Modal.Body>
          {fileType ? (
            <>
              {fileType === FileType.IMAGE && (
                <img
                  className={""}
                  src={fileUrl}
                  alt={`image "${data.filename}}`}
                />
              )}
              {fileType === FileType.VIDEO && (
                <video className={""} controls={true}>
                  <source src={fileUrl} type={VIDEO_TYPES_BY_EXT[fileExt]} />
                </video>
              )}
              {fileType === FileType.AUDIO && (
                <div className={"audio-wrapper"}>
                  <audio className={""} controls={true}>
                    <source src={fileUrl} type={AUDIO_TYPES_BY_EXT[fileExt]} />
                  </audio>
                </div>
              )}
              {fileType === FileType.PDF && (
                <div className={"pdf-wrapper"}>
                  <iframe
                    className={""}
                    src={`${fileUrl}#view=fit&page=1&toolbar=0&navpanes=0`}
                  />
                </div>
              )}
            </>
          ) : (
            <div className={"other-type-wrapper"}>
              This file type cannot be previewed.
              <br />
              Please download it, or open locally.
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <div className={"file-path"}>
            Local folder path:&nbsp;&nbsp;&nbsp;{data.unitDataFolder}
          </div>
        </Modal.Footer>
      </Modal>
    )
  );
}

export { InReviewFileModal };
