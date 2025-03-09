import { useEffect } from "react";
import { useSocketContext } from "@/context/SocketContext";
import { pathEndTurn } from "@/services/services";

export function useEndTurnSocket(gameId, playerId, setIsButtonActive) {
    const { socket } = useSocketContext();

    useEffect(() => {
        if (!socket) return;

        const handleNextTurnEvent = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === `${gameId}:NEXT_TURN`) {
                data.nextPlayerId == playerId ? setIsButtonActive(true) : setIsButtonActive(false);
            }
        };


        socket.addEventListener("message", handleNextTurnEvent);


        return () => {
            socket.removeEventListener("message", handleNextTurnEvent);
        };
    }, [socket, gameId, playerId, setIsButtonActive]);
}
