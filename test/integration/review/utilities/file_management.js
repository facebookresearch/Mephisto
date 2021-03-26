import fs from "fs";
import readLine from "readline";

export const fileAsArray = async (path, type) => {
  if (!path) return null;
  var lines = [];
  const readInterface = readLine.createInterface({
    input: fs.createReadStream(path),
    output: null,
    console: false,
  });
  for await (const line of readInterface) {
    if (type === "CSV") {
      lines.push(JSON.stringify(line.split(",")));
    } else {
      lines.push(line);
    }
  }
  return lines;
};
