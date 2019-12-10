import React from "react";
import "./TaskGallery.css";
import cx from "classnames";

import brace from "brace";
import AceEditor from "react-ace";
import "brace/mode/javascript";

const data_model = [
  {
    name: "QA Data Collection",
    desc:
      "Collect questions and answers from Turkers, given a random Wikipedia paragraph from SQuAD",
    tags: ["qa", "wikipedia", "SQuAD"]
  },
  {
    name: "Model Evaluator",
    desc:
      "Ask Turkers to evaluate the information retrieval baseline model on the Reddit movie dialog dataset",
    tags: ["reddit", "evaluate"]
  },
  {
    name: "Multi-Agent Dialog",
    desc: "Round-robin chat between a local human agent and two Turkers",
    tags: ["round-robin", "dialog"]
  },
  {
    name: "Deal or No Deal",
    desc:
      "Negotiation chat between two agents over how to fairly divide a fixed set of items when each agent values the items differently",
    tags: ["negotiation"]
  },
  {
    name: "Qualification Flow Example",
    desc:
      "Filter out workers from working on more instances of your task if they fail to complete a test instance properly",
    tags: ["example"]
  },
  {
    name: "Semantic Alignment",
    desc:
      "Allow Turkers to pick matching words between a pair of sentences based on some criteria",
    tags: ["sentences", "matching"],
    initialData: `{
  "text1": "Brad and Angelina tied the knot on Friday",
  "text2": "Angelina got married to Brad on Friday"
}`
  }
];

export default () => {
  const [selectedIndex, setSelectedIndex] = React.useState(null);
  const [searchTerm, setSearchTerm] = React.useState("");

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        maxWidth: 1440,
        width: "100%",
        margin: "0 auto",
        alignItems: "stretch",
        padding: "0 20px",
        boxSizing: "border-box"
      }}
    >
      <div
        className="card"
        style={{
          maxWidth: "none",
          width: "100%",
          minHeight: "300px",
          display: "flex"
        }}
      >
        <div className="task-list">
          <input
            className="search"
            placeholder="search..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
          {data_model.map(
            (task, idx) =>
              (searchTerm === "" ||
                task.name.match(new RegExp(searchTerm, "i")) ||
                task.tags.join(" ").match(new RegExp(searchTerm, "i"))) && (
                <div
                  className={cx("task-list-item", {
                    selected: idx === selectedIndex
                  })}
                  onClick={() => setSelectedIndex(idx)}
                >
                  <div className="name">{task.name}</div>
                  <div className="tags">
                    {task.tags.map(tag => (
                      <span>#{tag}</span>
                    ))}
                  </div>
                </div>
              )
          )}
        </div>{" "}
        {selectedIndex !== null && (
          <div className="task-description" key={selectedIndex}>
            <h1>{data_model[selectedIndex].name}</h1>
            <p>{data_model[selectedIndex].desc}</p>
            <div className="controls">
              <h3>
                Pass <code>task_data</code>:
              </h3>
              {/* <textarea /> */}
              <JSONEditor
                id={selectedIndex}
                initial={data_model[selectedIndex].initialData || ""}
              />
              <button className="btn inverse rounded">Submit</button>
            </div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 10
              }}
            >
              <h3>Live Example:</h3>
              <div>
                Viewing As:{" "}
                <select style={{ font: "inherit" }}>
                  <option>Worker</option>
                  <option>Teacher</option>
                  <option>Reviewer</option>
                </select>
              </div>
            </div>
            <iframe
              src="https://codesandbox.io/embed/x3oy3myvyp?fontsize=14&hidenavigation=1&view=preview"
              title="Paired Phrases Picker v0.1"
              style={{
                width: "100%",
                height: "500px",
                border: 0,
                borderRadius: "4px",
                overflow: "hidden"
              }}
              sandbox="allow-modals allow-forms allow-popups allow-scripts allow-same-origin"
            />
          </div>
        )}
      </div>
    </div>
  );
};

function JSONEditor({ initial, id }) {
  const [editorCode, setEditorCode] = React.useState("test");

  return (
    <div className="text-container">
      <AceEditor
        highlightActiveLine={false}
        value={initial}
        style={{
          backgroundColor: "transparent",
          padding: "10px",
          width: "100%",
          fontSize: 14,
          boxSizing: "border-box"
        }}
        mode="javascript"
        placeholder={"Type JSON payload here..."}
        tabSize={2}
        maxLines={Infinity}
        theme="tuesday"
        height="100px"
        showGutter={false}
        showPrintMargin={false}
        name={id}
        editorProps={{
          $blockScrolling: Infinity
        }}
      />
    </div>
  );
}
