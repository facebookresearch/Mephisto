import React from "react";

function Glyphicon({ name }) {
  return (
    <div className="icon-container">
      <span className={`glyphicon glyphicon-${name}`} aria-hidden="true" />
    </div>
  );
}

export default Glyphicon;
