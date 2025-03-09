import React, { useState, useEffect } from 'react';
import { startGame } from '@/services/services';
import { FaPlay } from 'react-icons/fa';
import { useLocation } from 'react-router-dom'

export default function StartButton({ gameId, isActive }) {
    const [showTooltip, setShowTooltip] = useState(false);
    const [error, setError] = useState('');
    const [showError, setShowError] = useState(false);
    const location = useLocation();

    useEffect(() => {
        setTimeout(() => setShowError(false), [1000])
    }, [showError, setShowError])


    const onStartClick = () => {
        if (isActive) {
            startGame(gameId)
                .catch(error => {
                    setError(error.message);
                    console.error(error);
                    setShowError(true);
                });
        }
    };
    return (
        <div className="relative w-100">
            <button
                onClick={onStartClick}
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
                className={` ${
                    isActive ? "text-green-400 cursor-pointer animate-pulse hover:scale-110 transition-transform" : "cursor-not-allowed text-zinc-700"
                }`}
                disabled={!isActive}
                data-testid="startButtonId"
            >
                <FaPlay size={40} color={`${isActive ? '' : ''}`}/>
            </button>

            {showTooltip && (
                <div className="absolute bottom-full mb-2 p-2 text-sm bg-gray-700 text-white rounded shadow-lg w-30">
                    Iniciar juego
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
