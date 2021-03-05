import React from "react";
import { H4, H3, Card, Elevation } from "@blueprintjs/core";
import WordCloud from "../components/WordCloud";
import "./css/WordCloudItemViewRenderer.css";

/*
    EXAMPLE PLUGIN ITEM RENDERER
    Renders mephisto review data items as word clouds of the most common words in the object
    For use inside an ItemView as an itemRenderer prop
*/
function WordCloudItemViewRenderer({ item }) {
  if (!item) return <p>No Data Available</p>;
  const data = item.data;
  const id = item.id;
  return (
    <Card className="word-cloud-item-view" elevation={Elevation.TWO}>
      <H4>
        <b>ID: {id}</b>
      </H4>
      <H3>Data keywords:</H3>
      {/*example WordCloud with example excluded keys and words*/}
      <WordCloud
        data={data}
        excludedKeys={["URL"]}
        excludedWords={[
          "true",
          "false",
          "the",
          "with",
          "on",
          "in",
          "of",
          "and",
        ]}
        minFontEmSize={1}
        maxFontEmSize={2.5}
        minFontWeight={100}
        maxFontWeight={700}
      />
    </Card>
  );
}

export default WordCloudItemViewRenderer;
