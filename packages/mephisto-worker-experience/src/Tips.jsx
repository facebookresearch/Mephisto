import React from "react";
import "./index.css";

function Tips({ list }) {
  const tipsComponents = list.map(
    (tip, index) => {
      return (
        <li key={`tip-${index + 1}`} className="tip">
          <h2 className="tip-header">{tip.header}</h2>
          <p>{tip.text}</p>
        </li>
      );
    },
    [list]
  );

  return <ul className="tips-list">{tipsComponents}</ul>;
}
export default Tips;
