import React, {useEffect} from 'react'

export function useOnClickOutside(refs, handler) {
  useEffect(
    () => {
      const listener = (event) => {
        // Do nothing if clicking ref's element or descendent elements
        let isClickOutside = true;
        for(let i = 0; i < refs.length; i++){
          if(refs[i].current && refs[i].current.contains(event.target)){
            isClickOutside = false
          }
          
        }
        if(isClickOutside){
          handler(event);
        }
        else return
      };
      document.addEventListener("mousedown", listener);
      document.addEventListener("touchstart", listener);
      return () => {
        document.removeEventListener("mousedown", listener);
        document.removeEventListener("touchstart", listener);
      };
    },
    // Add ref and handler to effect dependencies
    // It's worth noting that because passed in handler is a new ...
    // ... function on every render that will cause this effect ...
    // ... callback/cleanup to run every render. It's not a big deal ...
    // ... but to optimize you can wrap handler in useCallback before ...
    // ... passing it into this hook.
    [refs, handler]
  );
}