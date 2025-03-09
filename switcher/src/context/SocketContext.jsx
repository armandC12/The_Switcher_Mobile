import React, { createContext, useContext, useEffect, useState } from 'react';

const socketUrl = import.meta.env.VITE_SOCKET_URL.replace(/^http/, 'ws'); // Convert HTTP URL to WebSocket

export const SocketContext = createContext();  // Named export

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(socketUrl);  // Initialize WebSocket connection

    ws.onopen = () => {
      console.log('Connected to WebSocket');
    };

    ws.onmessage = (event) => {
      console.log('Message from server: ', event.data);
    };

    ws.onclose = () => {
      console.log('Disconnected from WebSocket');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error: ', error);
    };

    setSocket(ws);  // Save the WebSocket instance in state

    return () => {
      ws.close();  // Clean up WebSocket connection on unmount
    };
  }, []);  // Empty dependency array to initialize WebSocket once when the component mounts

  return (
    <SocketContext.Provider value={{ socket }}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocketContext = () => useContext(SocketContext);  // Named export
