var net = require('net');
var json = require('json');

var server = net.createServer(function(socket) {
  // The socket has been opened.
  console.log('Somebody connected');

  // Events
  socket.on('connect', function(){
    // This Code will be run when a new connection is opened
  });
  socket.on('data', function(data){
        console.log('Receiving data.');
    // Code here will be run when some data arrives
  });
  socket.on('end', function() {
    // Code here will be run when the socket closes
        console.log('Ending connection');
  });
});

// Start the server listening
server.listen(5432, function(){
  console.log('Server listening on port: ' + 5432);
});

var server = net.createServer(function(socket) {
  // The socket has been opened.
  console.log('Somebody connected');

  // Events
  socket.on('connect', function(){
    // This Code will be run when a new connection is opened
  });
  socket.on('data', function(data){
        console.log('Receiving data.');
        // Code here will be run when some data arrives
        // If the correct message was received, send a message.
        if data == 'GET':
            socket.write('Hello world!')
  });
  socket.on('end', function() {
    // Code here will be run when the socket closes
        console.log('Ending connection');
  });
});

// Start the server listening
server.listen(5433, function(){
  console.log('Server listening on port: ' + 5433);
});

