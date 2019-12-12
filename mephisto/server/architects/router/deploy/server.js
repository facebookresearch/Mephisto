/* Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
'use strict';

const bodyParser = require('body-parser');
const express = require('express');
const http = require('http');
const fs = require('fs');

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

const server = http.createServer(app);

server.listen(PORT, function() {
  console.log('Listening on %d', server.address().port);
});

// ===================== <Routing> ========================
app.get('/initial_task_data', function(req, res) {
  var params = req.query;
  var worker_id = params['worker_id']
  var assignment_id = params['assignment_id']
  var html_content = fs.readFileSync(task_directory_name + '/task.html', "utf8");
  // TODO hit the backend to get the actual assignment and worker
  // as registered
  var response_data = {
    worker_id: worker_id,
    assignment_id: assignment_id,
    html: html_content,
  }
  res.json(response_data)
});

// Quick status check for this server
app.get('/is_alive', function(req, res) {
  res.json({status: 'Alive!'});
});

// Returns server time for now
app.get('/get_timestamp', function(req, res) {
  res.json({ timestamp: Date.now() }); // in milliseconds
});

app.get('/task_index', function(req, res) {
  // TODO how do we pass the task config to the frontend?
  res.render('index.html');
});

app.use(express.static('static'));

// ======================= </Routing> =======================
