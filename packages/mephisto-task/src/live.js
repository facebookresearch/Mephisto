import { useMephistoTask } from "./index";

const useMephistoLiveTask = function () {
  const hookProps = useMephistoTask();
  const liveProps = {
    agentStatus: null,
    agentState: null,
    onNewData: () => {},
    postData: () => {},
    serverStatus: {},
  };

  return { ...hookProps, ...liveProps };
};

export { useMephistoLiveTask };
