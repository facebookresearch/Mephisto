#!/bin/sh
cd ../../packages/mephisto-task
npm install
npm run dev
cd ../../examples/static_react_task/webapp/
rm package-lock.json
npm install
npm link mephisto-task
npm run dev

