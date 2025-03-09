import React, { createContext, useState, useContext } from 'react';

const GameContext = createContext();

export const GameProvider = ({ children }) => {
  const [username, setUsername] = useState(`guest${Math.floor(Math.random() * (10000000000)) + 1}`); // nombre de usuario
  const [activeGameId, setActiveGameId] = useState(null); // id de la partida
  const [playerId, setPlayerId] = useState(null); // id del jugador
  const [players, setPlayers] = useState([]);
  const [gameName, setGameName] = useState(`game${Math.floor(Math.random() * (100000)) + 1}`);
  const [winnerName, setWinnerName] = useState('');
  const [currentTurn, setCurrentTurn] = useState(null);

  return (
    <GameContext.Provider value={{ username, setUsername, activeGameId, setActiveGameId, playerId, setPlayerId, players, setPlayers, gameName, setGameName, currentTurn, setCurrentTurn, winnerName, setWinnerName }}>
      {children}
    </GameContext.Provider>
  );
};

export const useGameContext = () => useContext(GameContext);
