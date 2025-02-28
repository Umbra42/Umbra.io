// init sockets
export function init() {
  const socket = io.connect(window.location.origin, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionAttempts: 3,
    reconnectionDelay: 1000,
  });

  socket.on('connect', () => {
    console.log('Connected to server');
  });
  
  socket.on('progress_update', (data) => {
    console.log('progress_update:', data);
    if (data.state === "completed") {
      console.log('Upload completed');
    } else if (data.state === 'error') {
      console.log(`Error: ${data.status}`);
    }
  });
  
  socket.on('disconnect', () => {
    console.log('Disconnected from server');
  });
  return socket;
}