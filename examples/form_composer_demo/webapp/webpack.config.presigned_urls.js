/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: "./src/presigned_urls.js",
  output: {
    path: __dirname,
    filename: "build/bundle.presigned_urls.js",
  },
  resolve: {
    alias: {
      react: path.resolve("./node_modules/react"),
      // Use local library with code that can submit FormData
      "mephisto-task-multipart": path.resolve(
        __dirname,
        "../../../packages/mephisto-task-multipart"
      ),
      // Use local library with code that can use FormComposer and  submit Worker Opinion
      "mephisto-task-addons": path.resolve(
        __dirname,
        "../../../packages/mephisto-task-addons"
      ),
    },
    fallback: {
      net: false,
      dns: false,
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        loader: "babel-loader",
        exclude: /node_modules/,
        options: { presets: ["@babel/env"] },
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(svg|png|jpe?g|ttf)$/,
        loader: "url-loader",
        options: { limit: 100000 },
      },
      {
        test: /\.jpg$/,
        loader: "file-loader",
      },
    ],
  },
  plugins: [new webpack.EnvironmentPlugin({ ...process.env })],
};
