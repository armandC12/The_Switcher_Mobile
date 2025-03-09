import { useSocketContext } from '@/context/SocketContext';
import { useEffect } from 'react';

export function useGameSocket(fetchGames, page, isFiltering, formData) {
  const { socket } = useSocketContext();

  useEffect(() => {
    if (!socket) return;

    const handleGamesListUpdate = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "GAMES_LIST_UPDATE") {
        fetchGames(page, formData);
      }
    };

    // Subscribe to WebSocket message events
    socket.addEventListener("message", handleGamesListUpdate);

    return () => {
      // Unsubscribe from WebSocket message events on cleanup
      socket.removeEventListener("message", handleGamesListUpdate);
    };
  }, [socket, fetchGames]);
}
