/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function ChatPane({ scrollBottomKey, children }) {
  const bottomAnchorRef = React.useRef(null);
  React.useEffect(() => {
    if (bottomAnchorRef.current) {
      bottomAnchorRef.current.scrollIntoView({
        block: "end",
        behavior: "smooth",
      });
    }
  }, [scrollBottomKey]);

  return (
    <div className="message-pane-segment">
      {children}
      <div className="bottom-anchor" ref={bottomAnchorRef} />
    </div>
  );
}

export default ChatPane;
