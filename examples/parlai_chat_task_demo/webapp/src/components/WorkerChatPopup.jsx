/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import {
  Button,
  Badge,
  Popover,
  Overlay,
  FormGroup,
  InputGroup,
  FormControl,
} from "react-bootstrap";

class WorkerChatPopup extends React.Component {
  // TODO: TO use this component, server-side functionality needs to be built
  // out to handle the worker-chat communication
  // https://github.com/facebookresearch/ParlAI/pull/1382

  constructor(props) {
    super(props);
    this.state = {
      hidden: true,
      msg: "",
    };
  }

  smoothlyAnimateToBottom() {
    if (this.bottomAnchorRef) {
      this.bottomAnchorRef.scrollIntoView({ block: "end", behavior: "smooth" });
    }
  }

  instantlyJumpToBottom() {
    if (this.chatContainerRef) {
      this.chatContainerRef.scrollTop = this.chatContainerRef.scrollHeight;
    }
  }

  componentDidMount() {
    this.instantlyJumpToBottom();
  }

  componentDidUpdate(prevProps, prevState) {
    // Use requestAnimationFrame to defer UI-based updates
    // until the next browser paint
    if (prevState.hidden === true && this.state.hidden === false) {
      requestAnimationFrame(() => {
        this.instantlyJumpToBottom();
      });
    } else if (prevProps.off_chat_messages !== this.props.off_chat_messages) {
      requestAnimationFrame(() => {
        this.smoothlyAnimateToBottom();
      });
    }
  }

  // TODO: Replace with enhanced logic to determine if the
  // chat message belongs to the current user.
  isOwnMessage = (message) => message.owner === 0;

  render() {
    const unreadCount = this.props.has_new_message;
    const messages = this.props.off_chat_messages || [];

    return (
      <div style={{ float: "right", marginRight: 7 }}>
        <Button
          onClick={() => this.setState({ hidden: !this.state.hidden })}
          ref={(el) => {
            this.buttonRef = el;
          }}
        >
          Chat Messages&nbsp;
          {!!unreadCount && (
            <Badge style={{ backgroundColor: "#d9534f", marginLeft: 3 }}>
              {unreadCount}
            </Badge>
          )}
        </Button>

        <Overlay
          rootClose
          show={!this.state.hidden}
          onHide={() => this.setState({ hidden: true })}
          placement="bottom"
          target={this.buttonRef}
        >
          <Popover id="chat_messages" title={"Chat Messages"}>
            <div
              className="chat-list"
              ref={(el) => {
                this.chatContainerRef = el;
              }}
              style={{ minHeight: 300, maxHeight: 300, overflowY: "scroll" }}
            >
              {messages.map((message, idx) => (
                <div
                  key={idx}
                  style={{
                    textAlign: this.isOwnMessage(message) ? "right" : "left",
                  }}
                >
                  <div
                    style={{
                      borderRadius: 4,
                      marginBottom: 10,
                      padding: "5px 10px",
                      display: "inline-block",
                      ...(this.isOwnMessage(message)
                        ? {
                            marginLeft: 20,
                            textAlign: "right",
                            backgroundColor: "#dff1d7",
                          }
                        : {
                            marginRight: 20,
                            backgroundColor: "#eee",
                          }),
                    }}
                  >
                    {message.msg}
                  </div>
                </div>
              ))}
              <div
                className="bottom-anchor"
                ref={(el) => {
                  this.bottomAnchorRef = el;
                }}
              />
            </div>
            <form
              style={{ paddingTop: 10 }}
              onSubmit={(e) => {
                e.preventDefault();
                if (this.state.msg === "") return;
                this.props.onMessageSend(this.state.msg);
                this.setState({ msg: "" });
              }}
            >
              <FormGroup>
                <InputGroup>
                  <FormControl
                    type="text"
                    value={this.state.msg}
                    onChange={(e) => this.setState({ msg: e.target.value })}
                  />
                  <InputGroup.Button>
                    <Button
                      className="btn-primary"
                      disabled={this.state.msg === ""}
                      type="submit"
                    >
                      Send
                    </Button>
                  </InputGroup.Button>
                </InputGroup>
              </FormGroup>
            </form>
          </Popover>
        </Overlay>
      </div>
    );
  }
}

export default WorkerChatPopup;
