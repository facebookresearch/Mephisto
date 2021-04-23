/**
 * collection of methods that can manage the file system during tests
 */
import fs from "fs";
import readLine from "readline";

/**
 * writes all lines of a given files as array elements line by line
 * mimicks behaviour of mephisto review server when reading files of specific types
 * @param {String} path path to file being read
 * @param {String} type type of file being read. Available types: "CSV"
 */
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
