var arDrone = require('ar-drone');
var http    = require('http');

var client = arDrone.createClient();

console.log('Connecting to AR Drone...');
console.log('Serving PNG stream on port 9000.');

var pngStream = arDrone.createClient().getPngStream();
var lastPng;
pngStream
    .on('error', console.log)
    .on('data', function(pngBuffer) {
        lastPng = pngBuffer;
    });

var server = http.createServer(function(req, res) {
    if (!lastPng) {
        res.writeHead(503);
        res.end('Did not receive any png data yet.');
        return;
    }

    res.writeHead(200, {'Content-Type': 'image/png'});
    res.end(lastPng);
});

server.listen(9000, function() {
    console.log('Serving latest PNG.');
});

console.log('Listening for JSON queries...');

var rl = require('readline');
var rl = rl.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', function(line) {
    // Make sure the parsed json file is valid.
    var query = JSON.parse(line)

    // Maybe figure out how to use pcmd and use that instead.
    if (query.turn) {
        client.clockwise(query.turn)
    }
    if (query.land) {
        client.land()
    }
    if (query.takeoff) {
        client.takeoff()
    }
}).on('close', function() {
    console.log('Exiting application.');
    process.exit(0);
});

