import { useEffect } from 'react';
import { useSocketContext } from '@/context/SocketContext'; // Asegúrate de que este path sea correcto

// Hook que escucha los eventos WebSocket y actualiza las cartas de movimiento
export function useUpdateCardsMovementSocket(gameId, playerId, fetchMovementCards) {
  const { socket } = useSocketContext(); // Extrae el socket del contexto

  useEffect(() => {
    if (!socket || !gameId || !playerId || !fetchMovementCards) return;

    // Manejador para los eventos de WebSocket
    const handleMovementUpdate = async (event) => {
      const data = JSON.parse(event.data);

      // Verifica si el mensaje es del tipo MOVEMENT_UPDATE y pertenece al gameId correcto
      if (data.type === `${gameId}:MOVEMENT_UPDATE` || data.type === `${gameId}:NEXT_TURN`) {
        // console.log("Mensaje de actualización de movimiento recibido", data);
        fetchMovementCards(); // Llama a la función para actualizar las cartas de movimiento
      }
    };

    // Agrega el listener para el evento de WebSocket
    socket.addEventListener('message', handleMovementUpdate);

    // Limpieza del listener cuando el componente se desmonta o cambian las dependencias
    return () => {
      socket.removeEventListener('message', handleMovementUpdate);
    };
  }, [socket, gameId, playerId, fetchMovementCards]); // Dependencias del hook
}
