/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: "./src/index.jsx",
  output: {
    path: __dirname,
    filename: "build/bundle.js",
    library: "mephisto-addons",
    libraryTarget: "umd",
  },
  target: "web",
  externals: {
    react: "react",
  },
  resolve: {
    alias: {
      // Use local library with code that can submit metadata with files
      "mephisto-core": path.resolve(__dirname, "../../packages/mephisto-core"),
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
        use: [
          {
            loader: "url-loader",
            options: {
              limit: 100000,
            },
          },
        ],
      },
      {
        test: /\.jpg$/,
        loader: "file-loader",
      },
    ],
  },
};
