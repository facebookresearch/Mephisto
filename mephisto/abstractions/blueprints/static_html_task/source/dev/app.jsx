/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { Button } from "react-bootstrap";
import { useMephistoTask, postData } from "mephisto-task";
const axios = require("axios");

/* global
  getWorkerName, getAssignmentId, getAgentRegistration, handleSubmitToProvider
*/

/* ================= Utility functions ================= */

function requestTaskHMTL(targetHtml) {
  var url = new URL(window.location.origin + "/" + targetHtml);
  return axios.get(url).then((res) => res.data);
}

/* ================= Application Components ================= */

function MainApp() {
  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
    isOnboarding,
    agentId,
    providerWorkerId,
  } = useMephistoTask();

  // We expose these as template variables, even if they aren't
  // directly asked for
  const MEPHISTO_KEY_MAP = {
    mephisto_agent_id: agentId,
    provider_worker_id: providerWorkerId,
  };

  function submitFromFrame(formData, objData) {
    if (isOnboarding) {
      handleSubmit(objData);
    } else {
      formData.append("USED_AGENT_ID", agentId);
      formData.append("final_string_data", JSON.stringify(objData));
      postData("/submit_task", formData)
        .then((data) => {
          handleSubmitToProvider(objData);
          return data;
        })
        .then(function (data) {
          console.table(objData);
        });
    }
  }

  if (blockedReason !== null) {
    return <h1>{blockedExplanation}</h1>;
  }
  if (isPreview) {
    return <ShowURL url="preview.html" />;
  }
  if (isLoading) {
    return <div>Loading..</div>;
  }
  if (isOnboarding) {
    return (
      <SubmitFrame onSubmit={submitFromFrame} currentTask={"onboarding"}>
        <ShowURL
          url={"onboarding.html"}
          data={initialTaskData}
          mephisto_keys={MEPHISTO_KEY_MAP}
        />
      </SubmitFrame>
    );
  }
  if (initialTaskData === null) {
    return <div>Loading...</div>;
  }
  return (
    <SubmitFrame onSubmit={submitFromFrame} currentTask={"main"}>
      <ShowURL
        url={initialTaskData["html"]}
        data={initialTaskData}
        mephisto_keys={MEPHISTO_KEY_MAP}
      />
    </SubmitFrame>
  );
}

function SubmitFrame({ children, onSubmit, currentTask }) {
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    // Reset submitting when switching from onboarding
    setSubmitting(false);
  }, [currentTask]);

  function handleFormSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    const formData = new FormData(event.target);
    let objData = {};
    formData.forEach((value, key) => {
      objData[key] = value;
    });
    onSubmit(formData, objData);
  }

  return (
    <div>
      <form encType="multipart/form-data" onSubmit={handleFormSubmit}>
        {children}
        <div>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <Button type="submit" disabled={submitting}>
              <span
                style={{ marginRight: 5 }}
                className="glyphicon glyphicon-ok"
              />
              {submitting ? "Submitting..." : "Submit"}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}

function ShowURL({ url, data = null, mephisto_keys = null }) {
  const [retrievedHtml, setRetrievedHtml] = React.useState(
    "<div>Loading..</div>"
  );

  React.useEffect(() => {
    if (url) {
      requestTaskHMTL(url).then((data) => setRetrievedHtml(data));
    }
  }, [url]);

  return (
    <HtmlRenderer
      html={retrievedHtml}
      data={data}
      mephisto_keys={mephisto_keys}
    />
  );
}

function HtmlRenderer({ html, data, mephisto_keys }) {
  const elRef = React.useRef();

  function handleUpdatingRemainingScripts(curr_counter, scripts_left) {
    if (scripts_left.length == 0) {
      return;
    }
    let script_to_load = scripts_left.shift();
    if (script_to_load.text == "") {
      var head = document.getElementsByTagName("head")[0];
      var script = document.createElement("script");
      script.onload = () => {
        handleUpdatingRemainingScripts(curr_counter + 1, scripts_left);
      };
      script.async = 1;
      script.src = script_to_load.src;
      head.appendChild(script);
    } else {
      const script_text = script_to_load.text;
      // This magic lets us evaluate a script from the global context
      (1, eval)(script_text);
      handleUpdatingRemainingScripts(curr_counter + 1, scripts_left);
    }
  }

  function interpolateHtml(html, dataObj = null) {
    let base_html = html;
    let fin_html = base_html;

    if (dataObj !== null) {
      for (let [key, value] of Object.entries(dataObj)) {
        let find_string = "${" + key + "}";
        // Could be better done with a regex for performant code
        fin_html = fin_html.split(find_string).join(value);
      }
    }

    if (mephisto_keys !== null) {
      // Add mephisto specific templates
      for (let [key, value] of Object.entries(mephisto_keys)) {
        let find_string = "${" + key + "}";
        fin_html = fin_html.split(find_string).join(value);
      }
    }

    return fin_html;
  }

  React.useEffect(() => {
    let children = elRef.current.children;
    let scripts_to_load = [];
    for (let child of children) {
      if (child.tagName == "SCRIPT") {
        scripts_to_load.push(child);
      }
    }
    if (scripts_to_load.length > 0) {
      handleUpdatingRemainingScripts(0, scripts_to_load);
    }
  }, [elRef.current]);

  return (
    <div
      ref={elRef}
      dangerouslySetInnerHTML={{ __html: interpolateHtml(html, data) }}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
