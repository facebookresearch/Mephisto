import React, { createContext, useContext, useReducer } from "react";
import lodash_set from "lodash.set";
import lodash_get from "lodash.get";
import lodash_unset from "lodash.unset";

const initialState = {
  __debug: {
    actionsFired: [],
  },
};

const Reducer = (state, action) => {
  const logAction = (action) => [...state.__debug.actionsFired, action];
  let newState;

  switch (action.type) {
    case "LAYER-SELECT":
      newState = { ...state, selectedLayer: action.payload };
      break;
    case "SET":
      newState = { ...state };
      lodash_set(newState, action.payload.key, action.payload.value);
      break;
    case "UNSET":
      // TODO: This method is untested!
      newState = { ...state };
      lodash_unset(newState, action.payload);
      break;
    case "INVOKE":
      console.log("invoke", action.payload.path);
      newState = { ...state };
      const prevValue = lodash_get(newState, action.payload.path);
      const nextValue = action.payload.fn(prevValue);
      lodash_set(newState, action.payload.path, nextValue);
      break;
    default:
      newState = state;
      break;
  }

  newState.__debug.actionsFired = logAction(action);
  return newState;
};
const Store = ({ children }) => {
  const [state, dispatch] = useReducer(Reducer, initialState);

  const set = (key, value) => {
    dispatch({ type: "SET", payload: { key, value } });
  };
  const get = React.useCallback(
    (key) => {
      return lodash_get(state, key);
    },
    [state]
  );
  const invoke = (path, fn) => {
    dispatch({ type: "INVOKE", payload: { path, fn } });
  };
  const unset = (key) => {
    dispatch({ type: "UNSET", payload: key });
  };

  const push = (path, value) => {
    if (!get(path)) {
      set(path, []);
    }
    invoke(path, (prev) => [...prev, value]);
  };

  return (
    <Context.Provider
      value={{ state, dispatch, set, get, invoke, unset, push }}
    >
      {children}
    </Context.Provider>
  );
};

export function useStore() {
  return useContext(Context);
}

export const Context = createContext(initialState);
export default Store;
