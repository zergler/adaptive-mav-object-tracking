#!/usr/bin/env node

var arDrone = require('ar-drone');
var client  = arDrone.createClient();
client.createRepl();

client.stop()
client.land()
