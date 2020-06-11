import React from "react";

const ChatContext = React.useContext(null);
const MephistoTaskContext = React.useContext(null);

function ChatContainer({ children }) {
  const [messages, dispatch] = React.useReducer((state, action) => {
    switch (action.type) {
      case "ADD":
        return [...state, action.payload];
      case "REMOVE":
        return state.filter((message) => message.id !== action.payload);
      case "REMOVE_ALL":
        return [];
      case "SET_METADATA":
        return state.map((message) =>
          message.id === action.payload.id
            ? { ...message, metadata: action.payload.metadata }
            : message
        );
      default:
        return state;
    }
  }, []);
  const fns = {
    add: (message) => dispatch({ type: "ADD", payload: message }),
    remove: (messageId) => dispatch({ type: "REMOVE", payload: messageId }),
    removeAll: () => dispatch({ type: "REMOVE_ALL" }),
    setMetadata: (messageId, metadata) =>
      dispatch({
        type: "SET_METADATA",
        payload: { id: messageId, metadata: metadata },
      }),
  };
  const props = { messages, ...fns };
  return <ChatContext.Provider value={props}>{children}</ChatContext.Provider>;
}

function useScene(sceneName) {}
function useDirector() {}

function BaseFrontend() {
  return <ChatContainer>Test</ChatContainer>;
}

export { BaseFrontend };
