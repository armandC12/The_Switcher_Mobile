import React, { useState } from "react";
import { useGameContext } from "@/context/GameContext";
import { useSocketContext } from "@/context/SocketContext";
import { blockCardFigure } from "@/services/services";
import { PiLockKeyDuotone } from "react-icons/pi";


export default function BlockCardFigureButton({ gameId, playerIdBlock, cardId, figure, resetBlock }) {
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

    const handleBlockedCardFigure = async () => {
        if (!gameId || !playerId) {
            handleError("No gameId or playerId")
            return;
        }
        try {
            const res = await blockCardFigure(gameId, playerId, playerIdBlock, cardId, figure);
            resetBlock(); // Llama a resetMov si la jugada es exitosa

            if(res.message === 'Invalid block card'){
                console.log(JSON.stringify(res))
                handleError('Bloqueo de carta inválido');
            }
            else{
                // logica para msg action
                socket.send(JSON.stringify(
                    {
                      type: `${gameId}:CHAT_MESSAGE`,
                      message: `${username} bloqueo una carta de figura.`
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
                onClick={handleBlockedCardFigure}
                disabled={!(figure.length!==0 && (playerId == currentTurn) && cardId)}
                className={`text-white ${(figure.length!==0 && (playerId == currentTurn) && cardId) ? 'animate-bounce' : 'opacity-50'}`}

                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
            >
                <PiLockKeyDuotone size={40} />
            </button>

            {showTooltip && (
                <div className="absolute bottom-full w-fit mb-2 z-50 p-2 text-sm bg-gray-700 text-white rounded">
                    Bloquear Carta
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
