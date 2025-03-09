import { useSocketContext } from "@/context/SocketContext";
import { useGameContext } from "@/context/GameContext";
import {act, useEffect} from "react";
import { calculateFigures, fetchTurnInfo } from "@/services/services";

export function useTurnInfoSocket(activeGameId, fetchBoard, setLoadingFig, setSyncEffect){
    const { socket } = useSocketContext();
    const {  playerId, currentTurn, setCurrentTurn } = useGameContext();

    useEffect(() => {
      if (!socket) return;
  
      const handleNextTurnEvent = async (event) => {
        const data = JSON.parse(event.data);
  
        if (data.type === `${activeGameId}:NEXT_TURN`) {
          fetchTurnInfo(activeGameId).then((newTurnData) => {
            if (newTurnData.current_player_id) {
              console.log(`old currentTurn: ${currentTurn}`);
              setCurrentTurn(newTurnData.current_player_id); // Correctly updates the state
            } else {
              console.error("Received an undefined player ID.");
            }
  
            // Fetch the board after the current turn is updated
            fetchBoard().then((res) => {
              if (newTurnData.current_player_id === playerId) {
                setSyncEffect(false);
                setLoadingFig(true);
  
                calculateFigures(activeGameId).then((res) => {
                  // setLoadingFig(false);
                  console.log(JSON.stringify(res));
                });
              }
            });
          })
          .catch((err) => console.log(err));
        }
      };
  
      socket.addEventListener("message", handleNextTurnEvent);
  
      return () => {
        socket.removeEventListener("message", handleNextTurnEvent);
      };
    }, [socket, activeGameId, setCurrentTurn, playerId, fetchBoard, setLoadingFig, setSyncEffect]);
    
    // Add a useEffect to log the updated currentTurn value
    useEffect(() => {
      console.log("Updated currentTurn:", currentTurn);
    }, [currentTurn]);
  
}