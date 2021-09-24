import React from "react";
import Store, { useStore } from "global-context-store";

export default {
  title: "Tests/global-context-store",
};

function CounterApp() {
  const { set, get } = useStore();

  React.useEffect(() => {
    set("counter", 0);
  }, []);

  const counter = get("counter");

  return (
    <div>
      <div
        style={{
          border: "1px solid #aaa",
          boxShadow: "0px 3px 3px 0px #ddd",
          display: "inline-block",
          padding: 10,
          marginBottom: "30px",
        }}
      >
        Counter: {counter}
        <div>
          <button
            onClick={() => set("counter", counter + 1)}
            style={{ marginTop: 10 }}
          >
            Increment
          </button>
        </div>
      </div>
    </div>
  );
}

export const RefForwarding = () => {
  const storeRef = React.useRef();
  return (
    <Store ref={storeRef}>
      <CounterApp />
      <button
        onClick={() => {
          const state = storeRef.current.getState();
          alert(JSON.stringify(state));
        }}
      >
        alert app state
      </button>
    </Store>
  );
};
