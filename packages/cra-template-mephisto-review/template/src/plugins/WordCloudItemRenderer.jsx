import React from "react";
import { H6 } from "@blueprintjs/core";
import WordCloud from "../components/WordCloud";

/*
    EXAMPLE PLUGIN ITEM RENDERER
    Renders mephisto review data items as word clouds of the most common words in the object
    For use inside an ItemListRenderer or AllItemView as an itemRenderer prop
*/
function WordCloudItemRenderer({ item }) {
  if (!item) return <p>No Data Available</p>;
  const data = item.data;
  const id = item.id;
  return (
    <div>
      <H6>
        <b>ID: {id}</b>
      </H6>
      <H6>Data keywords:</H6>
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
        minFontEmSize={0.4}
        maxFontEmSize={1.25}
        minFontWeight={200}
        maxFontWeight={600}
      />
    </div>
  );
}

export default WordCloudItemRenderer;
