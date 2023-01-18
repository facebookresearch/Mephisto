import React from "react";

import warningIcon from "./assets/icons/warning.svg";

const ActivityTrackerDisclosure = ({ title = "Warning", children }) => {
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
          {children}
        </div>
      </div>
    </div>
  );
};

export default ActivityTrackerDisclosure;
