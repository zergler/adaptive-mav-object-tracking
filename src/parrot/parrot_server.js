#!/usr/bin/env node

var arDrone = require('ar-drone');
var http    = require('http');
var net     = require('net');

console.log('Node js interface application for Parrot AR drone.')
console.log(':: Connecting to Parrot client.');
var client  = arDrone.createClient();
var pngPort = 9000;
var cmdPort = 9001;

// PNG stream from the drone.
console.log(':: Getting PNG stream from Parrot.')
var pngStream = arDrone.createClient().getPngStream();
var lastPng;
pngStream
    .on('error', console.log)
    .on('data', function(pngBuffer) {
        lastPng = pngBuffer;
    });

// Server that serves incoming png images onto port 9000.
console.log(':: Creating http server for serving received PNG stream.');
var pngServer = http.createServer(function(req, res) {
    if (!lastPng) {
        res.writeHead(503);
        res.end('Did not receive any png data yet.');
        return;
    }
    res.writeHead(200, {'Content-Type': 'image/png'});
    res.end(lastPng);
});

pngServer.listen(9000, function() {
    console.log(':: Serving PNG stream on port ' + pngPort + '.');
});


console.log(':: Creating socket net server for receiving commands.');
var cmdServer = net.createServer(function(socket) {
    // The socket has been opened.
    console.log('New connection from ' + socket.remoteAddress + ':' + socket.remotePort + '.');

    // This code will run when new data arives.
    socket.on('data', function(data){
        console.log('Receiving data...');
        var query;
        try {
            var query = JSON.parse(data);
            if (query.X > 0) {
                console.log('Receiving command to fly right at speed ' + query.X + '.')
                //client.right(query.X)
            }
            if (query.X < 0) {
                console.log('Receiving command to fly left at speed ' + query.X + '.')
                //client.left(Math.abs(query.X))
            }
            if (query.Y > 0) {
                console.log('Receiving command to fly forward at speed ' + query.Y + '.')
                //client.front(query.Y)
            }
            if (query.Y < 0) {
                console.log('Receiving command to fly backward at speed ' + query.Y + '.')
                //client.back(Math.abs(query.Y))
            }
            if (query.C > 0) {
                console.log('Receiving command to turn right at speed ' + query.C + '.')
            }
            if (query.T) {
                console.log('Receiving command to takeoff')
                //client.takeoff()
            }
            if (query.L) {
                console.log('Receiving command to land.')
                //client.land()
            }
        }
        catch (e) {
            // Parsed query is not a valid json object.
            console.log('Error: received query is not valid json.')
        }
    });

    // This code will run when the connection closes.
    socket.on('end', function() {
        console.log('Closing connection with ' + socket.remoteAddress + ':' + socket.remotePort + '.');
    });
});

// Start the server listening
cmdServer.listen(cmdPort, function(){
    console.log(':: Listening for commands on port ' + cmdPort + '.\n');
});
