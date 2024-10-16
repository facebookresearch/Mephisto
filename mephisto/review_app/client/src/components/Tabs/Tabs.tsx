import * as React from "react";
import { useEffect, useRef, useState } from "react";
import { Nav, Tab } from "react-bootstrap";
import "./Tabs.css";

type TabsPropsType = {
  activeTabName?: string;
  navClassName?: string;
  onPick?: (tabName: string) => void;
  tabs: TabType[];
};

let userKey = null;

function Tabs(props: TabsPropsType) {
  const { tabs, activeTabName } = props;

  const firstActiveTab = tabs.find((tab) => !tab.disabled);

  const [activeKey, setActiveKey] = useState<string>(
    activeTabName || firstActiveTab?.name
  );

  const tabContent = useRef(null);

  const onPick = (key: string) => {
    userKey = key;
    setActiveKey(key);
    props.onPick && props.onPick(key);
  };

  useEffect(() => {
    let tab = tabs.find((tab) => tab.name === userKey && !tab.disabled);
    if (!tab) {
      tab = tabs.find((tab) => !tab.disabled);
    }
    setActiveKey(activeTabName || tab.name);
  }, [tabs]);

  useEffect(() => {
    if (tabContent.current) {
      tabContent.current.scrollTop = 0;
    }
  });

  return (
    <div className={`tabs`}>
      {/* Tabs panel */}
      <Tab.Container activeKey={activeKey} onSelect={(k: string) => onPick(k)}>
        <Nav
          className={`
            tabs-nav
            ${props.navClassName || ""}
            ${props.tabs.length <= 1 ? "tabs-empty" : ""}
          `}
          variant={"tabs"}
        >
          {props.tabs.map((tab: TabType, i: number) => {
            return (
              <Nav.Item
                className={`
                  tabs-item
                  ${tab.disabled ? "disabled" : ""}
                `}
                key={i}
                title={
                  (tab.disabled ? tab.hoverTextDisabled : tab.hoverText) || null
                }
              >
                <Nav.Link
                  eventKey={tab.name}
                  className={`tabs-item-link`}
                  disabled={tab.disabled}
                >
                  {tab.title}
                </Nav.Link>
              </Nav.Item>
            );
          })}
        </Nav>

        {/* Selected tab content */}
        <Tab.Content className={`tabs-content`} ref={tabContent}>
          {props.tabs.map((tab: TabType, i: number) => {
            return (
              <Tab.Pane
                eventKey={tab.name}
                key={i}
                className={`tabs-content-pane no-margins`}
              >
                {tab.children}
              </Tab.Pane>
            );
          })}
        </Tab.Content>
      </Tab.Container>
    </div>
  );
}

export default Tabs;
