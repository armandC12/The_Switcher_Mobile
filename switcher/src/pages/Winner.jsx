import React from 'react';
import { useGameContext } from '../context/GameContext'; 
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import logo from '@/assets/logo_switcher.png';
import TYPE_1 from '../assets/images/fige01.svg';
import TYPE_4 from '../assets/images/fige04.svg';
import diagonalContiguo from '../assets/images/cruceDiagonalContiguo.svg';
import Lizquierda from '../assets/images/cruceEnLIzquierda.svg';

const Winner = () => {
  const { gameName, winnerName } = useGameContext(); // Obtener gameId y playerId del contexto
  const navigate = useNavigate();

  const handleGoToGames = () => {
    navigate('/games');
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-black text-white">
      {/* Logo izquierdo */}
      <div className="w-1/4 flex justify-center">
        <img className="h-80 w-auto" src={logo} alt="Logo" />
      </div>

      {/* Columna central con logo, cuadro e imágenes */}
      <div className="flex flex-col items-center mx-8 space-y-10">
        {/* Imágenes al lado del logo */}
        <div className="flex items-center space-x-4 mb-4">
          <img className="h-32 w-auto" src={TYPE_1} alt="TYPE_1" />
          <img className="h-32 w-auto" src={logo} alt="Logo" />
          <img className="h-32 w-auto" src={Lizquierda} alt="Lizquierda" />
        </div>

        {/* Cuadro central */}
        <div className="p-8 bg-gray-800 rounded-lg text-center">
          <h1 className="text-6xl font-bold mb-20">Winner</h1>
          <div className="mb-20">
            <h2 className="text-6xl">Partida: {gameName}</h2>
            <h2 className="text-6xl">Ganador: {winnerName}</h2>
          </div>
          <Button onClick={handleGoToGames} className="mt-4">
            Volver al inicio
          </Button>
        </div>

        <div className="flex items-center space-x-4 mb-4">
          <img className="h-32 w-auto" src={diagonalContiguo} alt="digonalContiguo" />
          <img className="h-32 w-auto" src={logo} alt="Logo" />
          <img className="h-32 w-auto" src={TYPE_4} alt="TYPE_4" />
        </div>
      </div>

      {/* Logo derecho */}
      <div className="w-1/4 flex justify-center">
        <img className="h-80 w-auto" src={logo} alt="Logo" />
      </div>
    </div>
  );
};

export default Winner;
