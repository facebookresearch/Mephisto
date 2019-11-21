/* Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
'use strict';

const bodyParser = require('body-parser');
const express = require('express');
const http = require('http');
const nunjucks = require('nunjucks');

const task_directory_name = 'static';

const PORT = process.env.PORT || 3000;

// Initialize app
const app = express();
app.use(bodyParser.text());
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
);
app.use(bodyParser.json());

nunjucks.configure(task_directory_name, {
  autoescape: true,
  express: app,
});

const server = http.createServer(app);

server.listen(PORT, function() {
  console.log('Listening on %d', server.address().port);
});

// Quick status check for this server
app.get('/is_alive', function(req, res) {
  res.json({status: 'Alive!'});
});

// Returns server time for now
app.get('/get_timestamp', function(req, res) {
  res.json({ timestamp: Date.now() }); // in milliseconds
});

app.use(express.static('static'));

// ======================= </Routing> =======================
