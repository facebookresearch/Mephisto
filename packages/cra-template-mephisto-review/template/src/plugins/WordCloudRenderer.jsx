import React from "react";
import { H4 } from "@blueprintjs/core";
import WordCloud from "../components/WordCloud";

/*
    EXAMPLE PLUGIN ITEM RENDERER
    Renders mephisto review data items as word clouds of the most common words in the object
*/
function WordCloudRenderer({ item }) {
  if (!item) return <p>No Data Available</p>;
  const data = item.data;
  const id = item.id;
  return (
    <div>
      <H4>
        <b>ID: {id}</b>
      </H4>
      <H4>Data keywords:</H4>
      <WordCloud
        data={data}
        filterKeys={["file"]}
        filterWords={[
          "#",
          "TIME_SEGMENTATION",
          "RESULT",
          "true",
          "false",
          "the",
          "with",
          "on",
          "in",
          "of",
          "and",
        ]}
      />
    </div>
  );
}

export default WordCloudRenderer;
