/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var webpackConfigure = require("@annotated/dev-scripts");

module.exports = webpackConfigure({ output: { library: "@annotated/shell" } });
