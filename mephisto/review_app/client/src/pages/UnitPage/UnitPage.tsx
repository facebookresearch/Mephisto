/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import InitialParametersCollapsable from "components/InitialParametersCollapsable/InitialParametersCollapsable";
import { InReviewFileModal } from "components/InReviewFileModal/InReviewFileModal";
import ResultsCollapsable from "components/ResultsCollapsable/ResultsCollapsable";
import TasksHeader from "components/TasksHeader/TasksHeader";
import VideoAnnotatorWebVTTCollapsable from "components/VideoAnnotatorWebVTTCollapsable/VideoAnnotatorWebVTTCollapsable";
import WorkerOpinionCollapsable from "components/WorkerOpinionCollapsable/WorkerOpinionCollapsable";
import {
  MESSAGES_IFRAME_DATA_KEY,
  MESSAGES_IN_REVIEW_FILE_DATA_KEY,
} from "consts/review";
import { setPageTitle } from "helpers";
import * as React from "react";
import { useEffect } from "react";
import { Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { getUnits, getUnitsDetails } from "requests/units";
import urls from "urls";
import "./UnitPage.css";

type ParamsType = {
  taskId: string;
  unitId: string;
};

interface UnitPagePropsType {
  setErrors: Function;
}

function UnitPage(props: UnitPagePropsType) {
  const params = useParams<ParamsType>();

  const iframeRef = React.useRef(null);

  const [iframeLoaded, setIframeLoaded] = React.useState<boolean>(false);
  const [iframeHeight, setIframeHeight] = React.useState<number>(100);
  const [unit, setUnit] = React.useState<UnitType>(null);
  const [loading, setLoading] = React.useState(false);

  const [unitDetails, setUnitDetails] = React.useState<UnitDetailsType>(null);

  const [unitInputsIsJSON, setUnitInputsIsJSON] = React.useState<boolean>(
    false
  );
  const [unitResultsIsJSON, setUnitResultsIsJSON] = React.useState<boolean>(
    false
  );

  const [inputsVisibility, setInputsVisibility] = React.useState<boolean>(null);
  const [resultsVisibility, setResultsVisibility] = React.useState<boolean>(
    null
  );
  const [inReviewFileModalShow, setInReviewFileModalShow] = React.useState<
    boolean
  >(false);
  const [inReviewFileModalData, setInReviewFileModalData] = React.useState<
    InReviewFileModalDataType
  >({});

  function getUnitDataFolder(): string {
    const unitDataFolderStartIndex = unitDetails.unit_data_folder.indexOf(
      "data/data"
    );
    const unitDataFolder = unitDetails.unit_data_folder.slice(
      unitDataFolderStartIndex
    );

    return unitDataFolder;
  }

  window.onmessage = function (e) {
    if (
      e.data &&
      e.type === "message" && // Waiting for `message` type only
      !e.data?.type // Exclude all unexpected messages from iframe
    ) {
      const data = JSON.parse(e.data);

      // Resize iframe message
      if (data.hasOwnProperty(MESSAGES_IFRAME_DATA_KEY)) {
        setIframeHeight(data[MESSAGES_IFRAME_DATA_KEY]["height"]);
      }
      // Open file field modal message
      else if (data.hasOwnProperty(MESSAGES_IN_REVIEW_FILE_DATA_KEY)) {
        const fieldname = data[MESSAGES_IN_REVIEW_FILE_DATA_KEY].fieldname;
        const filename = data[MESSAGES_IN_REVIEW_FILE_DATA_KEY].filename;
        const unitDataFolder = getUnitDataFolder();

        setInReviewFileModalData({
          fieldname: fieldname,
          filename: filename,
          title: filename,
          unitDataFolder: unitDataFolder,
          unitId: params.unitId,
        });
        setInReviewFileModalShow(true);
      }
    }
  };

  function onClickOnWorkerOpinionAttachment(file: WorkerOpinionAttachmentType) {
    const unitDataFolder = getUnitDataFolder();
    setInReviewFileModalData({
      fieldname: file.fieldname,
      filename: file.filename,
      requestByFilename: true,
      title: file.filename,
      unitDataFolder: unitDataFolder,
      unitId: params.unitId,
    });
    setInReviewFileModalShow(true);
  }

  function onError(errorResponse: ErrorResponseType | null) {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  }

  // [RECEIVING WIDGET DATA]
  // ---
  function sendDataToUnitIframe(data: object) {
    const reviewData = {
      REVIEW_DATA: {
        inputs: data["prepared_inputs"],
        outputs: data["outputs"],
      },
    };
    const unitIframe = iframeRef.current;
    unitIframe.contentWindow.postMessage(JSON.stringify(reviewData), "*");
  }
  // ---

  // Effects
  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Review - Current Unit");

    if (unit === null) {
      getUnits((units: UnitType[]) => setUnit(units[0]), setLoading, onError, {
        unit_ids: params.unitId,
      });

      getUnitsDetails(
        (unitsDetails: UnitDetailsType[]) => setUnitDetails(unitsDetails[0]),
        setLoading,
        onError,
        { unit_ids: params.unitId }
      );
    }
  }, []);

  useEffect(() => {
    if (unit) {
      // Update title with current unit
      setPageTitle(`Mephisto - Task Review - Unit ${unit.id}`);
    }
  }, [unit]);

  // [RECEIVING WIDGET DATA]
  // ---
  useEffect(() => {
    if (iframeLoaded && unitDetails?.has_task_source_review) {
      sendDataToUnitIframe(unitDetails);
    }
  }, [unitDetails, iframeLoaded]);
  // ---

  useEffect(() => {
    if (unitDetails) {
      const unitInputs = unitDetails.inputs;
      const unitOutputs = unitDetails.outputs;

      if (typeof unitInputs === "object") {
        setUnitInputsIsJSON(true);
      }

      if (typeof unitOutputs === "object") {
        setUnitResultsIsJSON(true);
      }

      // If Task expressly does not provide a preview template,
      // we just simply show JSON data for the Unit.
      // Change values only one time on loading page to save user choice
      if (unitDetails.has_task_source_review === false) {
        if (inputsVisibility === null) {
          setInputsVisibility(false);
        }
        if (resultsVisibility === null) {
          setResultsVisibility(true);
        }
      }
    }
  }, [unitDetails]);

  return (
    <div className={"unit"}>
      {/* Header */}
      <TasksHeader />

      {!loading && unit && (
        // Unit name
        <div className={"header"}>
          <div className={"unit-name"}>Unit: {unit.id}</div>

          <div>Task ID: {params.taskId}</div>

          <div>Worker ID: {unit.worker_id}</div>
        </div>
      )}

      <div className={"content"}>
        {/* Preloader when we request unit */}
        {loading && (
          <div className={"loading"}>
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        )}

        {/* Initial Unit parameters */}
        {unitDetails?.inputs && (
          <InitialParametersCollapsable
            data={unitDetails.inputs}
            open={inputsVisibility}
            isJSON={unitInputsIsJSON}
          />
        )}

        {/* Worker Opinion about Unit */}
        {unitDetails?.metadata?.worker_opinion && (
          <WorkerOpinionCollapsable
            data={unitDetails?.metadata?.worker_opinion}
            onClickOnAttachment={onClickOnWorkerOpinionAttachment}
          />
        )}

        {/* Video Annotator tracks in WebVTT format */}
        {unitDetails?.metadata?.webvtt && (
          <VideoAnnotatorWebVTTCollapsable
            data={unitDetails?.metadata?.webvtt}
            open={false}
          />
        )}

        {unitDetails?.outputs && (
          <>
            {/* Results */}
            <ResultsCollapsable
              data={unitDetails.outputs}
              open={resultsVisibility}
              isJSON={unitResultsIsJSON}
            />

            {/* Unit preview */}
            <div
              className={"unit-preview-container"}
              onClick={(e) => e.preventDefault()}
            >
              {unitDetails.has_task_source_review && (
                <iframe
                  className={"unit-preview-iframe"}
                  src={urls.server.unitReviewHtml(params.unitId)}
                  id={"unit-preview"}
                  title={"Completed Unit preview"}
                  height={iframeHeight} // Width is always 100% to receive correctly rendered height
                  onLoad={() => setIframeLoaded(true)}
                  ref={iframeRef}
                />
              )}
            </div>
          </>
        )}
      </div>

      {/* Modal to show preview of file fields */}
      <InReviewFileModal
        show={inReviewFileModalShow}
        setShow={setInReviewFileModalShow}
        data={inReviewFileModalData}
        setData={setInReviewFileModalData}
      />
    </div>
  );
}

export default UnitPage;
