/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
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
