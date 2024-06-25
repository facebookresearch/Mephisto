import { useEffect, useRef } from "react";
import * as React from "react";
import {
  ScaleBand,
  ScaleLinear,
  axisBottom,
  axisLeft,
  format,
  scaleBand,
  scaleLinear,
  select,
} from "d3";

interface HistogramPropsType {
  data: HistogramData[];
  height: number;
  width: number;
}

interface AxisBottomPropsType {
  scale: ScaleBand<string>;
  transform: string;
}

interface AxisLeftPropsType {
  maxValue: number;
  scale: ScaleLinear<number, number, never>;
}

interface BarsPropsType {
  data: HistogramPropsType["data"];
  height: number;
  scaleX: AxisBottomPropsType["scale"];
  scaleY: AxisLeftPropsType["scale"];
}

function truncateLabel(str, n) {
  return str.length > n ? str.slice(0, n - 1) + "..." : str;
}

function AxisBottom(props: AxisBottomPropsType) {
  const { scale, transform } = props;
  const ref = useRef<SVGGElement>(null);

  useEffect(() => {
    if (ref.current) {
      select(ref.current).call(axisBottom(scale));
    }
  }, [scale]);

  return <g ref={ref} transform={transform} />;
}

function AxisLeft(props: AxisLeftPropsType) {
  const { maxValue, scale } = props;
  const ref = useRef<SVGGElement>(null);

  const tickValues = Array.from({ length: maxValue + 1 }, (v, i) => i);

  useEffect(() => {
    if (ref.current) {
      select(ref.current).call(
        axisLeft(scale).tickValues(tickValues).tickFormat(format("d"))
      );
    }
  }, [scale]);

  return <g ref={ref} />;
}

function Bars(props: BarsPropsType) {
  const { data, height, scaleX, scaleY } = props;

  return (
    <>
      {data.map(({ value, label }) => (
        <rect
          key={`bar-${label}`}
          x={scaleX(label)}
          y={scaleY(value)}
          width={scaleX.bandwidth()}
          height={height - scaleY(value)}
          fill="#cbedec"
        />
      ))}
    </>
  );
}

export function Histogram(props: HistogramPropsType) {
  const { data, height, width } = props;
  const margin = { top: 20, right: 0, bottom: 20, left: 40 };
  const _width = width - margin.left - margin.right;
  const _height = height - margin.top - margin.bottom;

  const scaleX = scaleBand()
    .domain(data.map(({ label }) => truncateLabel(label, 25)))
    .range([0, _width])
    .padding(0.5);

  const maxScaleYValue = Math.max(...data.map(({ value }) => value));
  const scaleY = scaleLinear().domain([0, maxScaleYValue]).range([_height, 0]);

  return (
    <svg
      width={_width + margin.left + margin.right}
      height={_height + margin.top + margin.bottom}
    >
      <g transform={`translate(${margin.left}, ${margin.top})`}>
        <AxisBottom scale={scaleX} transform={`translate(0, ${_height})`} />
        <AxisLeft scale={scaleY} maxValue={maxScaleYValue} />
        <Bars data={data} height={_height} scaleX={scaleX} scaleY={scaleY} />
      </g>
    </svg>
  );
}
