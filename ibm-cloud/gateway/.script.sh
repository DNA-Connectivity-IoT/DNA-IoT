#!/bin/bash
node-red-stop
wget https://github.com/mikkopitkaenen/node-red-jasper-iot/archive/master.zip
unzip -oj ~/master.zip -d ~/.node-red/
rm -f ~/master.zip
npm install ~/.node-red/package.json
node-red-start &
