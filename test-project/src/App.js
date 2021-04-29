import React from "react"
import { MovableRect} from "annotation-toolkit"
import Store from "global-context-store";


function App() {

  const [ts, setTs] = React.useState(0);

  return (
    <Store>
      <h1>Isolated Bounding Box w/ Interpolation Test</h1>
      <h3>Current ts: {ts}</h3>
      <button onClick={() => { setTs(ts+1)}}>Next Frame</button> <button onClick={() => { setTs(ts - 1)}} >Prev Frame</button>
      <MovableRect defaultBox={[50, 200, 100, 100]} getTs={() => {
        return ts;
      }} />
    </Store>
  );
}

export default App;
