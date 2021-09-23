import React from "react";
import keyframes from "keyframes";
import cx from "classnames";
import ResizableRect from "./RRRR";
import { requestsPathFor, dataPathBuilderFor } from "./helpers";
import { useStore } from "global-context-store";

import "./RRRR/react-rect.css";
// import { FrameContextConsumer } from "react-frame-component";

export default function MovableRect({
  id,
  preload,
  document,
  getFrame,
  getLabel,
  defaultBox,
  fps = 30,
}) {
  const { get, set, push, state } = useStore();
  const k = React.useMemo(() => keyframes(), []);

  // TODO: Don't hardcode,
  const FPS = fps; // kept for now for backwards compat with AVD task,
  // in the future, by adding `on{Next,Previous,First,Last}Keyframe` methods,
  // we can make this component unaware of the VideoPlayer layer id and fps.

  // const layerInfo = useContext(LayerContext);
  // id = id || layerInfo?.id || undefined;

  const path = dataPathBuilderFor(id);
  const vidData = dataPathBuilderFor("Video");

  const isSelected = state.selectedLayer && state.selectedLayer[0] === id;

  const movable = !get(vidData("playing"));
  //   const getFrame = (get) => {
  //     const movable = !get(vidData("playing"));
  //     const playedSeconds = get(vidData("playedSeconds"));
  //     const currentFrame = Math.round(playedSeconds * FPS);
  //     const ts = movable ? currentFrame : currentFrame + 1;
  //     return ts;
  //   };

  const ts = getFrame(get);

  const vidLength = get(vidData("duration"));

  const DEFAULT_BOX = defaultBox || [10, 10, 100, 100]; // [top, left, width, height]

  const [boxState, setState] = React.useState({
    top: DEFAULT_BOX[0],
    left: DEFAULT_BOX[1],
    width: DEFAULT_BOX[2],
    height: DEFAULT_BOX[3],
  });

  const [lastFrame, setLastFrame] = React.useState();

  React.useEffect(() => {
    if (preload) {
      const length = preload.length;
      preload.forEach(({ x, y, width, height, frameNumber }, idx) => {
        const frame = {
          time: frameNumber,
          value: [x, y, width, height],
        };
        k.add(frame);
        if (idx === preload.length - 1) {
          setLastFrame(frame);
        }
      });
      set(path("kf"), k.frames);
    }
  }, []);

  const requestQueue = get(requestsPathFor(id));
  React.useEffect(() => {
    if (!requestQueue || requestQueue.length === 0) return;
    requestQueue.forEach((request) => {
      process(request);
    });
    set(requestsPathFor(id), []);
  }, [requestQueue]);
  const process = React.useCallback(
    (req) => {
      if (req.type === "prevKf") {
        const ts = getFrame(get);
        const prevTs = k.previous(ts);
        if (prevTs) {
          push(requestsPathFor("Video"), {
            type: "seek",
            payload: prevTs.time / FPS,
            // TODO: allow a FPS/seconds toggle?^
          });
        }
      } else if (req.type === "nextKf") {
        const ts = getFrame(get);
        const nextTs = k.next(ts);
        if (nextTs) {
          push(requestsPathFor("Video"), {
            type: "seek",
            payload: nextTs.time / FPS,
            // TODO: allow a FPS/seconds toggle?^
          });
        }
      } else if (req.type === "firstKf") {
        push(requestsPathFor("Video"), {
          type: "seek",
          payload: k.frames[0].time / FPS,
          // TODO: allow a FPS/seconds toggle?^
        });
      } else if (req.type === "lastKf") {
        push(requestsPathFor("Video"), {
          type: "seek",
          payload: k.frames[k.frames.length - 1].time / FPS,
          // TODO: allow a FPS/seconds toggle?^
        });
      } else if (req.type === "addFrame" || req.type === "addFrameAt") {
        // 1. get interpolated values
        const ts = req.payload || getFrame(get);
        const val = k.value(ts);
        const isKeyframe = k.getIndex(ts) >= 0;
        const [left, top, width, height] =
          val === null ? DEFAULT_BOX : val.map((x) => Math.round(x));

        // 2. create/update keyframe here with interpolate values:
        let idx = k.getIndex(ts);
        while (idx >= 0) {
          k.splice(idx, 1);
          idx = k.getIndex(ts);
        }
        k.add({
          time: ts,
          value: [left, top, width, height],
        });
        set(path("kf"), k.frames);

        // if a last frame was set and the user intentionally set a keyframe after that, blow out the lastFrame designation
        if (lastFrame && ts > lastFrame.time) {
          // TODO: this may be incorrect, we may unintentionally trigger this due to resolution errors
          // setLastFrame(null)

          //TODO: alternatively, instead of blowing out the lastFrame designation, we could promote the current frame as that instead
          setLastFrame({ time: ts, value: [left, top, width, height] });
        }
      } else if (req.type === "removeFrame") {
        let idx = k.getIndex(ts);
        while (idx >= 0) {
          k.splice(idx, 1);
          idx = k.getIndex(ts);
        }
        set(path("kf"), k.frames);
      } else if (req.type === "setFirst") {
        // Summary: set a keyframe at current time with interpolated values, and delete all previous keyframes

        // 1. get interpolated values
        const ts = getFrame(get);
        const val = k.value(ts);
        const isKeyframe = k.getIndex(ts) >= 0;
        const [left, top, width, height] =
          val === null ? DEFAULT_BOX : val.map((x) => Math.round(x));

        // 2. create/update keyframe here with interpolate values:
        let idx = k.getIndex(ts);
        while (idx >= 0) {
          k.splice(idx, 1);
          idx = k.getIndex(ts);
        }
        k.add({
          time: ts,
          value: [left, top, width, height],
        });

        // 3. remove all keyframes before this one:
        k.splice(0, k.getIndex(ts));

        // 4. Update data state
        set(path("kf"), k.frames);
      } else if (req.type === "setLast") {
        // Summary: set a keyframe at current time with interpolated values, and delete all future keyframes

        // 1. get interpolated values
        const ts = getFrame(get);
        const val = k.value(ts);
        const isKeyframe = k.getIndex(ts) >= 0;
        const [left, top, width, height] =
          val === null ? DEFAULT_BOX : val.map((x) => Math.round(x));

        // 2. create/update keyframe here with interpolate values:
        let idx = k.getIndex(ts);
        while (idx >= 0) {
          k.splice(idx, 1);
          idx = k.getIndex(ts);
        }
        k.add({
          time: ts,
          value: [left, top, width, height],
        });

        // 3. remove all keyframes after this one:
        k.splice(k.getIndex(ts) + 1, k.frames.length - k.getIndex(ts) - 1);

        // 4. Update data state
        set(path("kf"), k.frames);
        setLastFrame({
          time: ts,
          value: [left, top, width, height],
        });
      }
    },
    [k, get]
  );

  React.useEffect(() => {
    if (vidLength) {
      const ts = getFrame(get);
      if (preload) return;
      k.add({ time: ts, value: DEFAULT_BOX });
      // k.add({ time: vidLength, value: DEFAULT_BOX });
      set(path("kf"), k.frames);
    }
  }, [vidLength]);

  const handleResize = (style, isShiftKey, type) => {
    // type is a string and it shows which resize-handler you clicked
    // e.g. if you clicked top-right handler, then type is 'tr'
    let { top, left, width, height } = style;
    top = Math.round(top);
    left = Math.round(left);
    width = Math.round(width);
    height = Math.round(height);
    setState({
      ...boxState,
      top,
      left,
      width,
      height,
    });
    if (!movable) return;
    let idx = k.getIndex(ts);
    while (idx >= 0) {
      k.splice(idx, 1);
      idx = k.getIndex(ts);
    }
    k.add({
      time: ts,
      value: [left, top, width, height],
    });
    set(path("kf"), k.frames);
    if (state.selectedLayer.join("|") !== id) {
      set(["selectedLayer"], [id]);
    }
  };

  // const handleRotate = (rotateAngle) => {
  //   setState({ ...state, rotateAngle });
  // };

  const handleDrag = (deltaX, deltaY) => {
    if (!movable) return;

    const val = k.value(ts);
    const [left, top, width, height] =
      val === null
        ? [boxState.top, boxState.left, boxState.height, boxState.width]
        : val.map((x) => Math.round(x));

    setState({
      left: left + deltaX,
      top: top + deltaY,
      width,
      height,
    });
    let idx = k.getIndex(ts);
    while (idx >= 0) {
      k.splice(idx, 1);
      idx = k.getIndex(ts);
    }
    k.add({
      time: ts,
      value: [left + deltaX, top + deltaY, width, height],
    });
    set(path("kf"), k.frames);
    set(["selectedLayer"], [id]);
  };

  const handleSelect = () => {
    set(["selectedLayer"], [id]);
  };

  const isKeyframe = k.getIndex(ts) >= 0;

  const val = k.value(ts);
  const [left, top, width, height] =
    val === null ? DEFAULT_BOX : val.map((x) => Math.round(x));

  React.useEffect(() => {
    if (movable) {
      // same logic as below, can probably extract into a fn:
      if (ts < k.frames[0] && k.frames[0].time) {
        set(path("dim"), null);
      } else if (lastFrame && ts > lastFrame.time) {
        set(path("dim"), null);
      } else {
        set(path("dim"), [left, top, width, height]);
      }
    }
  }, [left, top, width, height, ts]);

  if (k.frames.length > 0) {
    if (ts < k.frames[0].time) {
      return null;
    } else if (lastFrame && ts > lastFrame.time) {
      return null;
    } /* else if (ts > k.frames[k.frames.length - 1].time) {
        return null;
      } */
  }

  return (
    <div
      className={cx(
        "movable-rect-frame",
        { keyframe: isKeyframe },
        { immovable: !movable },
        { selected: isSelected }
      )}
    >
      {!getLabel ? null : (
        <div
          style={{
            position: "absolute",
            left: left,
            top: top,
            backgroundColor: "white",
            color: "black",
            zIndex: 99,
          }}
        >
          {getLabel(get)}
        </div>
      )}
      <ResizableRect
        document={document || window.document}
        left={left}
        top={top}
        width={width}
        height={height}
        rotateAngle={0}
        // aspectRatio={false}
        // minWidth={10}
        // minHeight={10}
        zoomable="n, w, s, e, nw, ne, se, sw"
        rotatable={false}
        // onRotateStart={handleRotateStart}
        // onRotate={handleRotate}
        // onRotateEnd={handleRotateEnd}
        // onResizeStart={handleResizeStart}
        onResize={handleResize}
        // onResizeEnd={handleUp}
        onDragStart={handleSelect}
        onDrag={handleDrag}
        // onDragEnd={handleDragEnd}
      />
    </div>
  );
}

export function getInterpolatedFrames(allKeyframes) {
  let result = [];
  const kf = keyframes();
  allKeyframes.forEach(kf.add.bind(kf));

  if (allKeyframes.length === 0 || kf.frames.length === 0) {
    throw new Error(
      "MovableRect.getAllFrames() received invalid input data. Ensure keyframes exist."
    );
  }

  const firstKf = kf.frames[0].time;
  const lastKf = kf.frames[kf.frames.length - 1].time;

  if (firstKf > lastKf) {
    throw new Error(
      "MovableRect.getAllFrames() received invalid input data. First keyframe is after last keyframe."
    );
  }

  // console.groupCollapsed(layerName)
  for (let currentFrame = firstKf; currentFrame <= lastKf; currentFrame++) {
    const frame = kf.value(currentFrame);
    const rescaledValue = frame.map((x) => Math.round(x));
    result.push({ frame: currentFrame, value: rescaledValue });
  }
  return result;
}
