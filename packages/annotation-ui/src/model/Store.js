import React, { createContext, useContext, useReducer } from "react";
import lodash_set from "lodash.set";
import lodash_get from "lodash.get";
import lodash_invoke from "lodash.invoke";

const initialState = {
  srcVideo: "/assets/test.mp4",
  debug: {
    actionsFired: [],
  },
};

const Reducer = (state, action) => {
  const logAction = (action) => [...state.debug.actionsFired, action];
  let newState;

  switch (action.type) {
    case "SET-PROGRESS":
      newState = { ...state, progress: action.payload };
      break;
    case "SET-DURATION":
      newState = { ...state, duration: action.payload };
      break;
    case "LAYER-SELECT":
      newState = { ...state, selectedLayer: action.payload };
      break;
    case "SET":
      newState = { ...state };
      lodash_set(newState, action.payload.key, action.payload.value);
      break;
    case "INVOKE":
      console.log("invoke", action.payload.path);
      newState = { ...state };
      const prevValue = lodash_get(newState, action.payload.path);
      lodash_set(newState, action.payload.path, action.payload.fn(prevValue));
      break;
    default:
      newState = state;
      break;
  }

  newState.debug.actionsFired = logAction(action);
  return newState;
};
const Store = ({ children }) => {
  const [state, dispatch] = useReducer(Reducer, initialState);

  const set = (key, value) => {
    dispatch({ type: "SET", payload: { key, value } });
  };
  const get = (key) => {
    return lodash_get(state, key);
  };
  const invoke = (path, fn) => {
    dispatch({ type: "INVOKE", payload: { path, fn } });
  };

  return (
    <Context.Provider value={{ state, dispatch, set, get, invoke }}>
      {children}
    </Context.Provider>
  );
};

export function useStore() {
  return useContext(Context);
}

export const Context = createContext(initialState);
export default Store;
