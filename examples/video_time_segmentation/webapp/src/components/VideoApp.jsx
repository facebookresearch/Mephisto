import React from "react";
import ReactPlayer from "react-player";
import { useMephistoReview } from "mephisto-review-hook";

import "./VideoApp.css";

// import { mockData } from "./mock-data";

function VideoApp({ filePath, annotationData, onSubmit }) {
  const { data, isFinished, isLoading, submit, error } = useMephistoReview({
    mock: {
      useMock: true,
      data: {
        file: filePath /*"https://scontent-iad3-1.xx.fbcdn.net/v/t66.37151-6/10000000_1381580158719933_5095088059993314648_n.mp4?_nc_cat=102&ccb=2&_nc_sid=5f5f54&_nc_ohc=brc2uCDHQqEAX9TkJ_h&_nc_ht=scontent-iad3-1.xx&_nc_rmd=260&_nc_log=1&oh=dec7d5927e9c9b6080bcd79ab52a980e&oe=5FD12897",*/,
        info: annotationData,
      },
      isFinished: false,
      isLoading: false,
      submit: () => onSubmit(payload),
      error: null,
    },
  });
  console.log(data);
  const file = data?.file;
  const segData = data?.info;

  const [isModifiable, setIsModifiable] = React.useState(true);

  const [progress, setProgress] = React.useState(null);
  const [duration, setDuration] = React.useState(null);
  const [playing, setPlaying] = React.useState(false);
  const [pauseOnScrub, setPauseOnScrub] = React.useState(true);
  const [payload, setPayload] = React.useState(segData.payload);

  const vidRef = React.useRef();

  return (
    <div>
      {error && <div>{JSON.stringify(error)}</div>}
      {isLoading ? (
        <h1>Loading...</h1>
      ) : isFinished ? (
        <h1>Done reviewing!</h1>
      ) : (
        <div>
          <div className="app-container">
            <div className="video-viewer">
              <div style={{ textAlign: "center", marginBottom: 10 }}>
                <button
                  className="button"
                  onClick={() => {
                    submit({});
                  }}
                >
                  Next Video >
                </button>
              </div>
              <ReactPlayer
                url={file}
                controls
                playing={playing}
                onSeek={() => setPlaying(pauseOnScrub ? false : true)}
                onPlay={() => setPlaying(true)}
                onPause={() => setPlaying(false)}
                ref={vidRef}
                width={"100%"}
                progressInterval={350}
                onProgress={({ playedSeconds }) => {
                  setProgress(playedSeconds);
                }}
                onDuration={setDuration}
              />
              <label>
                <input
                  type="checkbox"
                  checked={pauseOnScrub}
                  onClick={() => setPauseOnScrub(!pauseOnScrub)}
                />{" "}
                Pause on scrub
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={isModifiable}
                  onClick={() => setIsModifiable(!isModifiable)}
                />{" "}
                Is Modifiable?
              </label>
              {isModifiable ? (
                <EditableSegment
                  currentTimeSeconds={progress}
                  duration={duration}
                  onSeek={(time) =>
                    vidRef?.current && vidRef.current.seekTo(time, "seconds")
                  }
                  onCommit={(newSegment) => {
                    console.log(newSegment);
                    const newPayload = [...payload, newSegment];
                    console.log(newPayload);
                    setPayload(newPayload);
                  }}
                />
              ) : null}
              <h3>Active annotations:</h3>
              {payload.map((seg, idx) =>
                progress >= seg.start_time &&
                progress <= Math.floor(seg.end_time) ? (
                  <Segment
                    isDeletable={isModifiable}
                    onDelete={() =>
                      setPayload(payload.filter((_, s_idx) => idx !== s_idx))
                    }
                    segment={seg}
                    duration={duration}
                    progress={progress}
                    onClick={() => {
                      vidRef?.current &&
                        vidRef.current.seekTo(seg.start_time, "seconds");
                    }}
                  />
                ) : null
              )}
            </div>
            <div className="segment-viewer">
              <h3>All annotations:</h3>
              {payload.map((seg, idx) => (
                <Segment
                  isDeletable={isModifiable}
                  onDelete={() =>
                    setPayload(payload.filter((_, s_idx) => idx !== s_idx))
                  }
                  segment={seg}
                  duration={duration}
                  isActive={
                    progress >= seg.start_time && progress <= seg.end_time
                  }
                  onClick={() => {
                    vidRef?.current &&
                      vidRef.current.seekTo(seg.start_time, "seconds");
                    setPlaying(true);
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function EditableSegment({ currentTimeSeconds, duration, onCommit, onSeek }) {
  const [startTime, setStartTime] = React.useState(null);
  const [endTime, setEndTime] = React.useState(null);
  const [label, setLabel] = React.useState("");

  const handleCommit = React.useCallback(() => {
    onCommit({
      end_time: Math.floor(endTime),
      start_time: Math.floor(startTime),
      label: label,
    });
    setStartTime(null);
    setEndTime(null);
    setLabel("");
  }, [onCommit, setStartTime, setEndTime, setLabel, endTime, startTime, label]);

  const startTimeDisplay =
    Math.floor(startTime / 60) +
    ":" +
    Math.floor(startTime % 60)
      .toString()
      .padStart(2, "0");
  const endTimeDisplay =
    Math.floor(endTime / 60) +
    ":" +
    Math.floor(endTime % 60)
      .toString()
      .padStart(2, "0");

  return (
    <div
      className={"segment-wrapper noninteractive"}
      style={{ margin: "40px 0" }}
    >
      <div className="seek-controls" style={{ margin: "0 0 10px 0" }}>
        <button
          onClick={() => {
            onSeek(Math.max(currentTimeSeconds - 5, 0));
          }}
        >
          -5x &#9194;
        </button>
        <button
          onClick={() => {
            onSeek(Math.max(currentTimeSeconds - 1, 0));
          }}
        >
          -1x ◀️
        </button>{" "}
        <button
          onClick={() => {
            onSeek(Math.min(currentTimeSeconds + 1, duration));
          }}
        >
          +1x ▶️
        </button>
        <button
          onClick={() => {
            onSeek(Math.min(currentTimeSeconds + 5, duration));
          }}
        >
          +5x &#9193;
        </button>
      </div>
      <span style={{ width: 230, display: "inline-block", fontWeight: "bold" }}>
        Current Video Time:{" "}
        {Math.floor(currentTimeSeconds / 60) +
          ":" +
          Math.floor(currentTimeSeconds % 60)
            .toString()
            .padStart(2, "0")}
      </span>
      <button
        onClick={() => setStartTime(currentTimeSeconds)}
        style={{
          border: "1px solid #aaa",
          backgroundColor: startTime !== null ? "#dedede" : "#fff",
        }}
      >
        Set as Start Time{startTime !== null ? ` (${startTimeDisplay})` : null}
      </button>
      <button
        onClick={() => setEndTime(currentTimeSeconds)}
        style={{
          border: "1px solid #aaa",
          backgroundColor: endTime !== null ? "#dedede" : "#fff",
        }}
      >
        Set as End Time{endTime !== null ? ` (${endTimeDisplay})` : null}
      </button>
      <div className="duration">
        <span>{startTimeDisplay}</span> &mdash; <span>{endTimeDisplay}</span>
        &nbsp;({(endTime - startTime).toFixed(1)}s)
      </div>
      <DurationTrack
        duration={duration}
        startTime={startTime}
        endTime={endTime}
      />
      <div>
        <textarea
          style={{ width: "100%" }}
          placeholder="Describe this time segment here..."
          value={label}
          onChange={(e) => {
            setLabel(e.target.value);
          }}
        ></textarea>
      </div>
      <button
        onClick={handleCommit}
        disabled={startTime === null || endTime === null || label === ""}
      >
        Commit
      </button>
    </div>
  );
}

function Segment({
  segment,
  onClick,
  duration,
  isActive = false,
  isDeletable = false,
  onDelete,
}) {
  return (
    <div
      className={"segment-wrapper " + (isActive ? "active" : "inactive")}
      onClick={onClick}
    >
      <div className="duration">
        <span>
          {Math.floor(segment.start_time / 60)}:
          {(segment.start_time % 60).toString().padStart(2, "0")}
        </span>{" "}
        &mdash;{" "}
        <span>
          {Math.floor(segment.end_time / 60)}:
          {(segment.end_time % 60).toString().padStart(2, "0")}
        </span>
        &nbsp;({segment.end_time - segment.start_time}s)
      </div>
      <DurationTrack
        duration={duration}
        startTime={segment.start_time}
        endTime={segment.end_time}
      />
      {isDeletable ? (
        <span
          style={{
            float: "right",
            fontSize: 12,
            marginLeft: 10,
            cursor: "pointer",
            fontWeight: "bold",
          }}
          onClick={() => {
            if (
              window.confirm(
                "Are you sure you'd like to delete this annotation?"
              )
            ) {
              onDelete && onDelete(segment);
            }
          }}
        >
          Delete
        </span>
      ) : null}
      <div className="segment">{segment.label}</div>
    </div>
  );
}

function DurationTrack({ duration, startTime, endTime }) {
  return (
    <div className="track">
      {duration && (
        <div
          className="bar"
          style={{
            width: (100 * (endTime - startTime)) / duration + "%",
            marginLeft: (100 * startTime) / duration + "%",
          }}
        ></div>
      )}
    </div>
  );
}

export default VideoApp;
