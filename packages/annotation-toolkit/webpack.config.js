/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var path = require("path");
var webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  entry: "./src/index.js",
  output: {
    path: __dirname,
    filename: "build/bundle.js",
    library: "annotation-toolkit",
    libraryTarget: "umd",
  },
  target: "web",
  externals: {
    react: "react",
    "react-dom": "react-dom",
    "global-context-store": "global-context-store",
    "@blueprintjs/core": "@blueprintjs/core",
    "@blueprintjs/icons": "@blueprintjs/icons",
  },
  node: {
    net: "empty",
    dns: "empty",
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "build/[name].css",
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        loader: "babel-loader",
        exclude: /node_modules/,
        options: { presets: ["@babel/env"] },
      },
      {
        test: /\.*css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.(svg|png|jpe?g|ttf)$/,
        loader: "url-loader?limit=100000",
      },
      {
        test: /\.jpg$/,
        loader: "file-loader",
      },
      {
        test: /\.(ttf|eot)$/,
        use: {
          loader: "ignore-loader",
        },
      },
      {
        test: /\.(woff|woff2)$/,
        use: {
          loader: "ignore-loader",
        },
      },
    ],
  },
};
