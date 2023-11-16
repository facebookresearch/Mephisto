import React from "react";

import warningIcon from "./assets/icons/warning.svg";

const ActivityTrackerDisclosure = ({
  title = "Your activity when interacting with this task is tracked over the complete duration of the task, not just the content that is submitted",
  children,
}) => {
  let content = children;
  if (!children) {
    content = (
      <dl>
        <dd>
          - We will record the answers you provide to the questions after
          providing each answer.
        </dd>
        <dd>
          - We will track various online behaviours related to your activity on
          our study’s web page, including how long you spend on each task, the
          mouse clicks you make and the quantity of scrolling you do on each
          page, and so forth.
        </dd>
        <dd>
          - We will collect some demographic information about you to enable a
          picture of our participant group as a whole. When you are completing
          your tasks, for example, we may collect your location data, age group,
          etc.
        </dd>
        <dd>
          - We will also collect information about your digital environment like
          your device version, operating system, browser version, IP addresses
          and cookie data, etc.
        </dd>
      </dl>
    );
  }

  return (
    <div
      style={{
        padding: "15px 10px",
        backgroundColor: "#FFF4E5",
        borderRadius: "5px",
        display: "flex",
      }}
    >
      <div style={{ padding: "5px" }}>
        <img src={warningIcon} alt="warningIcon" style={{ width: "16px" }} />
      </div>
      <div
        style={{
          padding: "5px",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          color: "#663C00",
        }}
      >
        <div
          style={{
            fontWeight: 500,
            fontSize: "16px",
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontSize: "14px",
          }}
        >
          {content}
        </div>
      </div>
    </div>
  );
};

export default ActivityTrackerDisclosure;
