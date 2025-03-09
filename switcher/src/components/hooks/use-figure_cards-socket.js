import { useEffect } from "react";
import { useSocketContext } from "@/context/SocketContext";

export function useFigureCardsSocket(gameId, getFigureCards, getTurnInfo) {
    const { socket } = useSocketContext();

    useEffect(() => {
        if (!socket) return;

        const handleNextTurnEvent = (event) => {
            const data = JSON.parse(event.data);

            
            if (data.type === `${gameId}:FIGURE_UPDATE` || data.type === `${gameId}:NEXT_TURN` || data.type === `${gameId}:UNDOBLOCK_CARD`) {
                getFigureCards();
                getTurnInfo(gameId);
            } 
        };

        
        socket.addEventListener("message", handleNextTurnEvent);

        
        return () => {
            socket.removeEventListener("message", handleNextTurnEvent);
        };
    }, [socket, gameId, getFigureCards]);
}
