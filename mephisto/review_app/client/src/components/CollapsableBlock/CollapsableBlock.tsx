/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { useEffect } from 'react';
import * as React from "react";
import "./CollapsableBlock.css";


type CollapsableBlockPropsType = {
  children: any;
  className?: string;
  open?: boolean;
  title: string | React.ReactElement;
  tooltip?: string;
};

function CollapsableBlock(props: CollapsableBlockPropsType) {
  const { children, className, open, title, tooltip } = props;

  const [openContent, setOpenContent] = React.useState<boolean>(open);

  const headerTooltip = tooltip || "Toggle data";

  useEffect(() => {
    setOpenContent(open);
  }, [open]);

  return (
    <>
      <div className={`collapsable-block ${className || ""}`}>
        <div
          className={"collapsable-block-header"}
          onClick={() => setOpenContent(!openContent)}
          title={headerTooltip}
        >
          {title}
          <i className={"collapsable-block-icon"}>
            {openContent ? <>&#x25BE;</> : <>&#x25B8;</>}
          </i>
        </div>

        <div className={`${openContent ? "" : "collapsable-block-closed"}`}>
          {children}
        </div>
      </div>
    </>
  );
}

export default CollapsableBlock;
