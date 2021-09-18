/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var path = require("path");
var webpack = require("webpack");
const merge = require("webpack-merge").merge;
const paths = require("./paths");
const PnpWebpackPlugin = require(`pnp-webpack-plugin`);

const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const baseConfig = {
  entry: "./src/index.js",
  output: {
    path: paths.appBuild,
    filename: "bundle.js",
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
  resolve: {
    plugins: [PnpWebpackPlugin],
    // This allows you to set a fallback for where webpack should look for modules.
    // We placed these paths second because we want `node_modules` to "win"
    // if there are any conflicts. This matches Node resolution mechanism.
    // https://github.com/facebook/create-react-app/issues/253
    modules: ["node_modules", paths.appNodeModules].concat(
      /*modules.additionalModulePaths*/ [] || []
    ),
  },
  resolveLoader: {
    plugins: [PnpWebpackPlugin.moduleLoader(module)],
  },
  node: {
    net: "empty",
    dns: "empty",
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "[name].css",
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        loader: require.resolve("babel-loader"),
        exclude: /node_modules/,
        options: {
          presets: [
            require.resolve("@babel/preset-env"),
            require.resolve("@babel/preset-react"),
          ],
        },
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

const productionConfig = {};
const developmentConfig = {};

module.exports = (options) => (env) => {
  const isProduction = env === "production";
  const isDevelopment = env === "development";
  const environmentConfig = isProduction ? productionConfig : developmentConfig;

  const config = merge(baseConfig, environmentConfig, options);

  // Apply any final options based on the merged config.
  const extraConfig = {
    mode: isProduction
      ? "production"
      : isDevelopment
      ? "development"
      : "production", // default fallback env
    plugins: [
      // Set NODE_ENV based on the provided Webpack environment.
      new webpack.DefinePlugin({
        NODE_ENV: JSON.stringify(isProduction ? "production" : "development"),
      }),
    ],
  };

  return merge(config, extraConfig);
};
