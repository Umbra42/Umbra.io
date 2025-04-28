// init sockets
console.log("⚙ sockets.js loaded");
export function init() {
  const socket = io('/upload',{
    transports: ['websocket'],
    reconnectionAttempts: 3,
  });

  socket.on('connect', () => {
    console.log('Connected to server/upload, socket.id =', socket.id);
  });
  
  socket.on('disconnect', () => {
    console.log('Disconnected from /upload');
  });
  return socket;
}