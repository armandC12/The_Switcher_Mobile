import React, { useState } from "react";
import { useGameContext } from "@/context/GameContext";
import { claimFigure } from "@/services/services";
import { useSocketContext } from "@/context/SocketContext";

import { TbLayoutGridAdd } from "react-icons/tb";
import { BsGridFill } from "react-icons/bs";


export default function ClaimFigureButton({ gameId, cardId, figure, resetFigureSelection }) {
    const { playerId, currentTurn } = useGameContext();
    const [showTooltip, setShowTooltip] = useState(false);
    const [showError, setShowError] = useState(false);
    const [error, setError] = useState(null);
    const {username} = useGameContext();
    const {socket} = useSocketContext();
    const handleError = (errorMessage) => {
        console.error(errorMessage);
        setError(errorMessage);
        setShowError(true);
        setTimeout(() => {
            setShowError(false);
            setError(null);
        }, 1000)
    }

    const handleClaimFigure = async () => {
        // console.log("HOLAAAA")
        if (!gameId || !playerId) {
            handleError("No gameId or playerId")
            return;
        }
        try {
            console.log(`Voy a jugar la carta ${cardId} con la figura del tablero ${JSON.stringify(figure)}`);
            const res = await claimFigure(gameId, playerId, cardId, figure);

            resetFigureSelection(); // Llama a resetMov si la jugada es exitosa

            if(res.message === 'Invalid figure'){
                console.log(JSON.stringify(res))
                handleError('Figura inválida');
            }
            else{
                // logica para msg action
                socket.send(JSON.stringify(
                    {
                      type: `${gameId}:CHAT_MESSAGE`,
                      message: `${username} reclamo una figura.`
                    }
                  ))
            }
        }
        catch (error) {
            handleError(error.message);
        }
    };


    return (
        <div className="relative">
            <button
                data-testid = 'claimButtonTestId'
                onClick={handleClaimFigure}
                disabled={!(figure.length!==0 && (playerId == currentTurn) && cardId)}
                className={`text-white ${(figure.length!==0 && (playerId == currentTurn) && cardId) ? 'animate-bounce' : 'opacity-50'}`}

                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
            >
                <BsGridFill size={40} />
            </button>

            {showTooltip && (
                <div className="absolute bottom-full w-fit mb-2 z-50 p-2 text-sm bg-gray-700 text-white rounded">
                    Reclamar figura
                </div>
            )}

            {showError && (
                <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-600 text-white p-4 rounded shadow-md z-50">
                    {error}
                </div>
            )}
        </div>
    );
}
