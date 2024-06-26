import * as d3 from "d3";
import * as React from "react";
import { useEffect, useMemo } from "react";

const MARGIN = { top: 30, right: 30, bottom: 30, left: 120 };

const BAR_PADDING = 0.2;

const TRUNCATE_LABEL_LENGTH = 20;

function truncateLabel(text: string, n: number): string {
  return text.length > n ? text.slice(0, n - 1) + "..." : text;
}

interface HistogramPropsType {
  className?: string;
  data: HistogramData[];
  width: number;
}

export function Histogram(props: HistogramPropsType) {
  const { className, width, data } = props;

  // bounds = area inside the graph axis = calculated by substracting the margins
  const calculatedHeight = data?.length * 40;
  const boundsWidth = width - MARGIN.right - MARGIN.left;
  const boundsHeight = calculatedHeight - MARGIN.top - MARGIN.bottom;

  // Y axis is for groups since the barplot is horizontal
  const groups = data
    .sort((a, b) => b.value - a.value)
    .map((d: HistogramData) => truncateLabel(d.label, TRUNCATE_LABEL_LENGTH));

  const yScale = useMemo(() => {
    return d3
      .scaleBand()
      .domain(groups)
      .range([0, boundsHeight])
      .padding(BAR_PADDING);
  }, [data, calculatedHeight]);

  // X axis
  const xScale = useMemo(() => {
    const [min, max] = d3.extent(data.map((d: HistogramData) => d.value));
    return d3
      .scaleLinear()
      .domain([0, max || 10])
      .range([0, boundsWidth]);
  }, [data, width]);

  // Build the shapes
  const allShapes = data.map((d: HistogramData, i: number) => {
    const truncatedLabel = truncateLabel(d.label, TRUNCATE_LABEL_LENGTH);

    const y = yScale(truncatedLabel);
    if (y === undefined) {
      return null;
    }

    return (
      <g key={i}>
        <rect
          x={xScale(0)}
          y={yScale(truncatedLabel)}
          width={xScale(d.value)}
          height={yScale.bandwidth()}
          opacity={1}
          stroke="#cbedec"
          fill="#cbedec"
          fillOpacity={1}
          strokeWidth={1}
          rx={1}
        />
        <text
          x={xScale(d.value) + 8}
          y={y + yScale.bandwidth() / 2}
          textAnchor="start"
          alignmentBaseline="central"
          fontSize={12}
          opacity={1}
        >
          {d.value}
        </text>
        <text
          className={"label"}
          x={xScale(0) - 8}
          y={y + yScale.bandwidth() / 2}
          textAnchor="end"
          alignmentBaseline="central"
          fontSize={12}
          data-label={d.label}
        >
          {truncatedLabel}
        </text>
      </g>
    );
  });

  useEffect(() => {
    d3.selectAll(".label")
      .on("mouseover", (e) => {
        // TODO: Fix logic of showing tooltip
        const label = d3.select(e.target).text();
        const fullLabel = d3.select(e.target).attr("data-label");
        const coordinates = d3.pointer(e);

        if (label !== fullLabel) {
          d3.selectAll(`.${className} .tooltip`)
            .html(fullLabel)
            .attr("x", coordinates[0] - 20)
            .attr("y", coordinates[1] - 20)
            .style("visibility", "visible");
        }
      })
      .on("mouseout", (e) => {
        d3.selectAll(".tooltip").style("visibility", "hidden");
      });
  }, []);

  return (
    <div className={className}>
      <svg width={width} height={calculatedHeight}>
        <g
          width={boundsWidth}
          height={boundsHeight}
          transform={`translate(${[MARGIN.left, MARGIN.top].join(",")})`}
        >
          {allShapes}

          <text
            className={"tooltip"}
            style={{
              visibility: "hidden",
              color: "black",
            }}
            fontSize={12}
          ></text>
        </g>
      </svg>
    </div>
  );
}
