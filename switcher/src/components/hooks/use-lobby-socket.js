import { useSocketContext } from '@/context/SocketContext';
import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

export function useLobbySocket(gameId, fetchGameInfo) {
  const { socket } = useSocketContext();  // Get WebSocket instance
  const navigate = useNavigate();
  const {playerId} = useParams();
  useEffect(() => {
    if (!socket) return;

    // Define a function to handle incoming messages
    const handleGameInfoUpdate = (event) => {
      const data = JSON.parse(event.data);  // Assuming server sends JSON data
      if (data.type === `${gameId}:GAME_INFO_UPDATE`) {
        fetchGameInfo();
      }

      if (data.type === `${gameId}:GAME_STARTED`) {
        navigate(`/games/ongoing/${gameId}/${playerId}`);
      }

      // si el owner abandona el lobby, redirigir a los jugadores a la pantalla de juegos
      if (data.type === `${gameId}:OWNER_LEFT`) {
        navigate('/games');
      }
    };

    // Subscribe to WebSocket message events
    socket.addEventListener("message", handleGameInfoUpdate);

    return () => {
      // Unsubscribe from WebSocket message events on cleanup
      socket.removeEventListener("message", handleGameInfoUpdate);
    };
  }, [socket, fetchGameInfo]);  // Dependency array includes socket and fetchGames
}
