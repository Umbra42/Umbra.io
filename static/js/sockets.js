// init sockets
export function init() {
  const socket = io({
    transports: ['websocket'],
    reconnectionAttempts: 3,
  });

  socket.on('connect', () => {
    console.log('Connected to server');
  });
  
  socket.on('disconnect', () => {
    console.log('Disconnected from server');
  });
  return socket;
}