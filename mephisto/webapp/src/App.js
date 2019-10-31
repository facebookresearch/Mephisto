import React from "react";
import Sidebar from "./Sidebar";
import DetailPane from "./DetailPane";

function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-page">
        <div className="app-page-header">
          <h1>Dashboard</h1>
          {/* <input type="text" name="search" placeholder="Search.." /> */}
        </div>
      </div>
      <DetailPane />
    </div>
  );
}

export default App;
