const express = require('express')
const http = require('http')
const WebSocket = require('ws')
const udp = require('dgram')

const app = express()
app.use(express.static(__dirname+'/webimu2/'));
const httpServer = http.createServer(app)
const wss = new WebSocket.Server({
  'server': httpServer
});

const udpserver = udp.createSocket('udp4');

wss.on('connection', ws => {
  ws.on('message', message => {
    console.log(`Received message => ${message}`)
  })
  ws.send('Hello! Message From Server!!')
});

udpserver.on('message',function(msg,info){
  console.log('Data received from client : ' + msg.toString());
  console.log('Received %d bytes from %s:%d\n',msg.length, info.address, info.port);
  wss.clients.forEach((client) => {
    client.send(msg.toString());
  });
});

udpserver.bind(8081);
httpServer.listen(8080);
