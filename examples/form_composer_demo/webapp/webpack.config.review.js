/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: "./src/review.js",
  output: {
    path: __dirname,
    filename: "build/bundle.review.js",
  },
  resolve: {
    alias: {
      react: path.resolve("./node_modules/react"),
      // Use local library with code that can submit FormData
      "react-form-composer": path.resolve(
        __dirname,
        "../../../packages/react-form-composer"
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
};
