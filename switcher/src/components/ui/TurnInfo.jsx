import React, { useEffect, useState } from 'react';
import { useTurnInfoSocket } from '../hooks/use-turn_info-socket';


const colors = ['text-red-500', 'text-blue-500', 'text-green-500', 'text-yellow-500'];

export default function TurnInformation({ players, activeGameId, currentTurn, setCurrentTurn }) {
  const [colorClass, setColorClass] = useState('');

  

  useEffect(() => {
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    setColorClass(randomColor);
  }, [currentTurn]);

  const currentPlayer = players.length > 0 ? players.find(player => player.id === currentTurn) : null;

  return (
    <div className="flex flex-col  justify-center items-center bg-zinc-900 text-white p-6 rounded-lg shadow-md border-2 border-zinc-700 space-y-6">
      <h2 className="text-2xl font-bold mb-4">Información del Turno</h2>
      <p className="text-md mb-2">
        Jugadores en la partida <span className="font-semibold">{players.length}</span>
      </p>
      <p className="text-md">
        Juega  
        <span className={`font-semibold ml-2 ${colorClass}`}>
          {currentPlayer ? currentPlayer.name : "Cargando..."}
        </span>
      </p>
      {/* <p className="text-md mb-2">
        Color prohibido: 
      </p> */}
    </div>
  );
}
