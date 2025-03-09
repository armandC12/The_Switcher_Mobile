import { useGameContext } from '@/context/GameContext';
import { useSocketContext } from '@/context/SocketContext';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function useActiveGameSocket(gameId, fetchPlayers) {
  const { socket } = useSocketContext();  
  const navigate = useNavigate();
  const {setWinnerName} = useGameContext();

  useEffect(() => {
    if (!socket) return;

    const handleGameInfoUpdate = (event) => {
      const data = JSON.parse(event.data);  
      if (data.type === `${gameId}:GAME_INFO_UPDATE`) {
        fetchPlayers();
      }

      if (data.type === `PLAYER_WINNER` && data.game_id == gameId) {
        setWinnerName(data.winner_name);
        navigate(`/games/winner`);
      }
    };

    // Subscribe to WebSocket message events
    socket.addEventListener("message", handleGameInfoUpdate);

    return () => {
      // Unsubscribe from WebSocket message events on cleanup
      socket.removeEventListener("message", handleGameInfoUpdate);
    };
  }, [socket, fetchPlayers]); 
}
