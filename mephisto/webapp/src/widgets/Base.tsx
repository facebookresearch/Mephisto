import React from "react";
import { Card, Elevation } from "@blueprintjs/core";

interface BaseProps {
  heading: React.ReactElement;
  badge: string | undefined;
}

export default (function BaseWidget({ children, heading, badge }) {
  return (
    <Card elevation={Elevation.THREE} className="widget">
      <h4 className="bp3-heading" style={{ marginBottom: 15 }}>
        {badge !== undefined && (
          <span className="bp3-tag bp3-large bp3-minimal bp3-round step-badge">
            {badge}
          </span>
        )}
        {heading}
      </h4>
      {children}
    </Card>
  );
} as React.FC<BaseProps>);
