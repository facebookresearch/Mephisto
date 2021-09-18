/**
 * Copyright (c) 2015-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const path = require("path");
const fs = require("fs");

// Make sure any symlinks in the project folder are resolved:
// https://github.com/facebook/create-react-app/issues/637
const appDirectory = fs.realpathSync(process.cwd());
const resolveApp = (relativePath) => path.resolve(appDirectory, relativePath);

module.exports = {
  appNodeModules: resolveApp("node_modules"),
  appPackageJson: resolveApp("package.json"),
  publicUrlOrPath: "",
  appPublic: resolveApp("public"),
  appHtml: resolveApp("public/index.html"),
  appBuild: resolveApp(process.env.BUILD_PATH || "build"),
};
