#!/usr/bin/env node

var arDrone = require('ar-drone');
var http    = require('http');
var net     = require('net');

console.log('Node js interface application for Parrot AR drone.')
console.log(':: Connecting to Parrot client.');

// Maybe specify frame rate and image size...
var client  = arDrone.createClient();
var cmdPort = 9000;
var recvPort = 9001;

// Server that listens for incoming commands for the drone.
console.log(':: Creating socket net server for receiving commands.');
var cmdServer = net.createServer(function(socket) {
    // The socket has been opened.
    console.log('New connection from ' + socket.remoteAddress + ':' + socket.remotePort + '.');

    // This code will run when new data arives.
    socket.on('data', function(data) {
        var query;
        try {
            var query = JSON.parse(data);
            if (query.X > 0) {
                console.log('Receiving command to fly right at speed ' + query.X + '.');
                client.right(query.X);
            }
            if (query.X < 0) {
                console.log('Receiving command to fly left at speed ' + Math.abs(query.X) + '.');
                client.left(Math.abs(query.X));
            }
            if (query.Y > 0) {
                console.log('Receiving command to fly forward at speed ' + query.Y + '.');
                client.front(query.Y);
            }
            if (query.Y < 0) {
                console.log('Receiving command to fly backward at speed ' + Math.abs(query.Y) + '.');
                client.back(Math.abs(query.Y));
            }
            if (query.Z > 0) {
                console.log('Receiving command to fly up at speed ' + query.Z + '.');
                client.up(query.Z);
            }
            if (query.Z < 0) {
                console.log('Receiving command to fly down at speed ' + Math.abs(query.Z) + '.');
                client.down(Math.abs(query.Z));
            }
            if (query.R > 0) {
                console.log('Receiving command to turn right at speed ' + query.R + '.');
                client.clockwise(query.R);
            }
            if (query.R < 0) {
                console.log('Receiving command to turn left at speed ' + Math.abs(query.R) + '.');
                client.counterClockwise(Math.abs(query.R));
            }
            if (query.T) {
                console.log('Receiving command to takeoff.');
                client.takeoff();
            }
            if (query.L) {
                console.log('Receiving command to land.');
                client.land();
            }
            if (query.C) {
                if (camera == 0) {
                    camera = 3;
                    console.log('Receiving command to serve the bottom camera stream');
                    client.config('video:video_channel', 3);
                }
                else if (camera == 3) {
                    camera = 0;
                    console.log('Receiving command to serve the front cammera stream');
                    client.config('video:video_channel', 0)
                }
            }
            if (query.S) {
                console.log('Receiving command to stop.');
                client.stop();
            }
        }
        catch (e) {
            // Parsed query is not a valid json object.
            console.log('Error: received query is not valid json.');
        }
    });

    // This code will run when the connection closes.
    socket.on('end', function() {
        console.log('Closing connection with ' + socket.remoteAddress + ':' + socket.remotePort + '.');
    });
});

// Start the server listening.
cmdServer.listen(cmdPort, function(){
    console.log(':: Listening for commands on port ' + cmdPort + '.');
});

// Server that listens for a 'GET' string and sends the drone's navigation data.
console.log(':: Creating socket net server for sending navigation data.');
var recvServer = net.createServer(function(socket) {
    // The socket has been opened.
    console.log('New connection from ' + socket.remoteAddress + ':' + socket.remotePort + '.');

    // This code will run when new data arives.
    socket.on('data', function(data) {
        var query;
        try {
            var query = JSON.parse(data);
            if (query === 'GET') {
                console.log('Received query to send navigation data.');
                socket.write(client.navdata)
            }
        }
        catch (e) {
            // Parsed query is not a valid json object.
            console.log('Error: received query is not valid json.');
        }

    });

    // This code will run when the connection closes.
    socket.on('end', function() {
        console.log('Closing connection with ' + socket.remoteAddress + ':' + socket.remotePort + '.');
    });
});

// Start the server listening.
recvServer.listen(recvPort, function(){
    console.log(":: Listening for query to send navigation data on port " + recvPort + '.');
});
