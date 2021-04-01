import React from "react";
import vqaData from "./vqa.json";
import groupBy from "lodash.groupby";
import mapValues from "lodash.mapvalues";
import { useStore } from "../model";

function prepareData(data) {
  let d = groupBy(data.payload, "label");
  d = mapValues(d, (val) => groupBy(val, "tags[0]"));
  return d;
}

function DataLoader() {
  const { set } = useStore();

  const video = {
    src:
      "https://interncache-ash.fbcdn.net/v/t53.39266-7/10000000_101490861881999_3097760480370384378_n.mp4?_nc_map=test-rt&ccb=1-3&_nc_sid=5f5f54&efg=eyJ1cmxnZW4iOiJwaHBfdXJsZ2VuX2NsaWVudC9pbnRlcm4vc2l0ZS94L2ZiY2RuIn0%3D&_nc_ht=interncache-ash&_nc_rmd=260&oh=83a2a653bb8d85f026a4eeab167b37f8&oe=607EE6EA",
    originalWidth: 1920,
    originalHeight: 1440,
    fps: 5,
  };
  const SCALE = 0.33;
  const initData = {
    ...video,
    scale: SCALE,
    width: video.originalWidth * SCALE,
    height: video.originalHeight * SCALE,
  };

  const data = prepareData(vqaData);

  React.useEffect(() => {
    set("taskData", data);
    set("initData", initData);
    set("selectedLayer", ["Query 1"]);
  }, []);

  return null;
}

export default DataLoader;
