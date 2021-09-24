import React from "react";
import merge from "lodash.merge";
import "./keypoints.css";

const includeRightArm = [
  ["r_shoulder", "r_elbow"],
  ["r_elbow", "r_wrist"],
];
const includeLeftArm = [
  ["l_shoulder", "l_elbow"],
  ["l_elbow", "l_wrist"],
];
const includeRightFoot = [["r_toetip", "r_ankle"]];
const includeLeftFoot = [["l_toetip", "l_ankle"]];
const includeHead = [
  ["head", "r_shoulder"],
  ["head", "l_shoulder"],
];

const does = (has, include) => {
  return has ? include : [];
};

const isIn = (name, arr) => {
  return arr.indexOf(name) >= 0;
};

export function Pose({
  imageHeight,
  imageWidth,
  hasHead,
  hasLeftArm,
  hasRightArm,
  hasLeftFoot,
  hasRightFoot,
}) {
  const [hoveredJoint, setHoveredJoint] = React.useState(null);
  const [isMoving, setIsMoving] = React.useState(false);

  const shouldShow = React.useCallback(
    (name) => {
      const shouldHide =
        (name === "head" && !hasHead) ||
        (isIn(name, ["l_wrist", "l_elbow"]) && !hasLeftArm) ||
        (isIn(name, ["r_wrist", "r_elbow"]) && !hasRightArm) ||
        (name === "l_toetip" && !hasLeftFoot) ||
        (name === "r_toetip" && !hasRightFoot);
      return !shouldHide;
    },
    [hasHead, hasLeftArm, hasRightArm, hasLeftFoot, hasRightFoot]
  );

  const basePose = React.useMemo(
    () => ({
      joints: {
        head: [0, 0],
        l_shoulder: [1, 1],
        l_elbow: [2, 1],
        l_wrist: [3, 1],
        r_shoulder: [-1, 1],
        r_elbow: [-2, 1],
        r_wrist: [-3, 1],
        l_hip: [1, 3],
        l_knee: [1, 4.5],
        l_ankle: [1, 6],
        l_toetip: [2, 6],
        r_hip: [-1, 3],
        r_knee: [-1, 4.5],
        r_ankle: [-1, 6],
        r_toetip: [-2, 6],
      },
      edges: [
        ["r_shoulder", "l_shoulder"],

        ["r_shoulder", "r_hip"],
        ["r_hip", "r_knee"],
        ["r_knee", "r_ankle"],

        ["r_hip", "l_hip"],

        ["l_shoulder", "l_hip"],
        ["l_hip", "l_knee"],
        ["l_knee", "l_ankle"],

        ...does(hasHead, includeHead),
        ...does(hasLeftArm, includeLeftArm),
        ...does(hasRightArm, includeRightArm),
        ...does(hasLeftFoot, includeLeftFoot),
        ...does(hasRightFoot, includeRightFoot),
      ],
    }),
    [hasHead, hasLeftArm, hasRightArm, hasLeftFoot, hasRightFoot]
  );

  const [pose, setPose] = React.useState(basePose);

  const updatedJoints = [
    ["r_shoulder", "l_shoulder"],

    ["r_shoulder", "r_hip"],
    ["r_hip", "r_knee"],
    ["r_knee", "r_ankle"],

    ["r_hip", "l_hip"],

    ["l_shoulder", "l_hip"],
    ["l_hip", "l_knee"],
    ["l_knee", "l_ankle"],

    ...does(hasHead, includeHead),
    ...does(hasLeftArm, includeLeftArm),
    ...does(hasRightArm, includeRightArm),
    ...does(hasLeftFoot, includeLeftFoot),
    ...does(hasRightFoot, includeRightFoot),
  ];

  React.useEffect(() => {
    setPose(Object.assign({}, pose, { edges: updatedJoints }));
  }, [hasHead, hasLeftArm, hasRightArm, hasLeftFoot, hasRightFoot]);

  const padding = 20;
  const yStep = (imageHeight - padding) / 7;
  const xStep = (imageWidth - padding) / 8;
  const mapX = (unit) => unit * xStep + imageWidth / 2;
  const mapY = (unit) => unit * yStep + padding;
  const unmapX = (coord) => (coord - imageWidth / 2) / xStep;
  const unmapY = (coord) => (coord - padding) / yStep;

  return (
    <div style={{ position: "relative" }}>
      <svg
        style={{ width: imageWidth, height: imageHeight }}
        viewBox={`0 0 ${imageWidth} ${imageHeight}`}
        xmlns="http://www.w3.org/2000/svg"
      >
        <g>
          {pose.edges.map(([from, to]) => (
            <>
              <Line
                key={`${from}-${to}-border`}
                x1={mapX(pose.joints[from][0])}
                y1={mapY(pose.joints[from][1])}
                x2={mapX(pose.joints[to][0])}
                y2={mapY(pose.joints[to][1])}
                stroke={
                  isMoving && [from, to].indexOf(hoveredJoint) >= 0
                    ? "black"
                    : "white"
                }
                strokeWidth="3"
              />
              <Line
                key={`${from}-${to}`}
                x1={mapX(pose.joints[from][0])}
                y1={mapY(pose.joints[from][1])}
                x2={mapX(pose.joints[to][0])}
                y2={mapY(pose.joints[to][1])}
                stroke={
                  isMoving && [from, to].indexOf(hoveredJoint) >= 0
                    ? "red"
                    : "black"
                }
                strokeWidth="1"
              />
            </>
          ))}
          {Object.entries(pose.joints).map(
            ([name, pos]) =>
              shouldShow(name) && (
                <Circle
                  key={name}
                  cx={mapX(pos[0])}
                  cy={mapY(pos[1])}
                  strokeWidth="2"
                  stroke="white"
                  r="4"
                  onPositionUpdate={(pos) => {
                    const newPos = [unmapX(pos.x), unmapY(pos.y)];
                    setPose(merge({}, pose, { joints: { [name]: newPos } }));
                    setIsMoving(pos.active);
                  }}
                  onHover={(enter) => {
                    setHoveredJoint(enter ? name : null);
                  }}
                />
              )
          )}
        </g>
      </svg>
      {hoveredJoint ? (
        <div className="tooltip">
          {hoveredJoint?.replace("l_", "left ")?.replace("r_", "right ")}
        </div>
      ) : null}
      <div className="debug">
        <strong>DEBUG:</strong>{" "}
        {Object.entries(pose.joints).map(([name, [x, y]]) => {
          return shouldShow(name) ? (
            <div key={name}>
              <span style={{ display: "inline-block", width: 80 }}>
                {name}:
              </span>{" "}
              {x.toPrecision(2)}, {y.toPrecision(2)}
            </div>
          ) : null;
        })}
      </div>
    </div>
  );
}

const Line = (props) => {
  return <line {...props} />;
};

const Circle = ({ cx, cy, onPositionUpdate, onHover, ...props }) => {
  // credit: https://gist.github.com/hashrock/0e8f10d9a233127c5e33b09ca6883ff4
  const [position, setPositionRaw] = React.useState({
    x: cx,
    y: cy,
    active: false,
    offset: {},
  });

  const setPosition = React.useCallback(
    (pos) => {
      onPositionUpdate(pos);
      setPositionRaw(pos);
    },
    [setPositionRaw, onPositionUpdate]
  );

  const handlePointerDown = (e) => {
    const el = e.target;
    const bbox = e.target.getBoundingClientRect();
    const x = e.clientX - bbox.left;
    const y = e.clientY - bbox.top;
    el.setPointerCapture(e.pointerId);
    setPosition({
      ...position,
      active: true,
      offset: {
        x,
        y,
      },
    });
  };
  const handlePointerMove = (e) => {
    const bbox = e.target.getBoundingClientRect();
    const x = e.clientX - bbox.left;
    const y = e.clientY - bbox.top;
    const movePosition = {
      ...position,
      x: position.x - (position.offset.x - x),
      y: position.y - (position.offset.y - y),
    };
    if (position.active) {
      setPosition(movePosition);
    }
  };
  const handlePointerEnter = () => {
    onHover(true);
  };
  const handlePointerLeave = () => {
    onHover(false);
  };
  const handlePointerUp = (e) => {
    setPosition({
      ...position,
      active: false,
    });
  };

  return (
    <circle
      cx={position.x}
      cy={position.y}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerMove={handlePointerMove}
      onPointerOut={handlePointerLeave}
      onPointerEnter={handlePointerEnter}
      {...props}
      fill={position.active ? "red" : "#aaa"}
    />
  );
};
