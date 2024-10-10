import * as React from "react";
import { Spinner } from "react-bootstrap";
import "./Preloader.css";

type PreloaderPropsType = {
  className?: string;
  loading: boolean;
};

function Preloader(props: PreloaderPropsType) {
  if (!props.loading) {
    return null;
  }

  return (
    <div className={`loading ${props.className ? props.className : ""}`}>
      <Spinner animation={"border"} role={"status"}>
        <span className={"visually-hidden"}>Loading...</span>
      </Spinner>
    </div>
  );
}

export default Preloader;
