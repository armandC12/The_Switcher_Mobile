import React, { useEffect, useState } from "react";
import { useGameContext } from "@/context/GameContext";
import { calculateFigures, pathEndTurn } from "@/services/services";
import { useEndTurnSocket } from "../hooks/use-end_turn-socket";
import {FaCheck} from 'react-icons/fa'
import { useSocketContext } from "@/context/SocketContext";
import { GiPlayerNext } from "react-icons/gi";
import { PiCheckFatFill } from "react-icons/pi";

const EndTurnButton = ({gameId, currentTurn, resetFigureSelection, resetMovement }) => {
  const [isButtonActive, setIsButtonActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const { playerId, username } = useGameContext();
  const [showTooltip, setShowTooltip] = useState(false);
  const {socket} = useSocketContext();

  useEffect(() => {
    if (currentTurn===playerId) {
      setIsButtonActive(true);
    }
  }, [currentTurn, playerId]);

  // Conexion con socket
  useEndTurnSocket(gameId, playerId, setIsButtonActive);

  // Manejar la lógica para terminar el turno
  const onHandleEndTurn = async () => {
    resetFigureSelection();
    resetMovement();
    setLoading(true);
    // setLoadingFig(true);

     pathEndTurn(gameId).then((res) => {

       if (!res) {
         console.error("Error actualizando el turno");
       }

      // logica para msg action
      socket.send(JSON.stringify(
        {
          type: `${gameId}:CHAT_MESSAGE`,
          message: `${username} paso de turno.`
        }
      ))


     }).catch(error => {
       console.error("Error al terminar el turno", error);
      })
      .finally(() => {
        setLoading(false);
        // setLoadingFig(false);
     })

  };

  return (
    <div className="relative">
      <button data-testid='endTurnButtonId' onClick={onHandleEndTurn} onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)} className={`text-white ${isButtonActive ? 'hover:scale-110 transition-transform' : 'opacity-50'}`}
      disabled={!isButtonActive || loading}>
            <PiCheckFatFill size={40} />
      </button>
      {showTooltip && (
        <div className="absolute bottom-full w-fit mb-2 z-50 p-2 text-sm bg-gray-700 text-white rounded">
            Finalizar turno
        </div>
      )}
    </div>
  );
};

export default EndTurnButton;
