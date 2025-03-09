import React, { useEffect, useState } from 'react';
import PlayersList from '../components/ui/PlayersList';
import { useParams, useLocation } from 'react-router-dom';
import { useGameContext } from '@/context/GameContext';
import { getPlayers, getGameInfo, getPlayer, startGame, calculateFigures } from '../services/services';
import { useLobbySocket } from '@/components/hooks/use-lobby-socket';
import BotonAbandonar from '@/components/ui/LeaveButton';
import Chat from '@/components/ui/chat';
import { useSocketContext } from '@/context/SocketContext';
import StartButton from '../components/ui/StartButton';

export default function Lobby() {
  const { gameId } = useParams();
  let {playerId} = useParams();
  playerId = Number(playerId);
  const { players, setPlayers, setPlayerId, gameName, setGameName, username, setUsername } = useGameContext();
  const [iniciateActive, setIniciateActive] = useState(false);
  const [maxPlayers, setMaxPlayers] = useState(0);
  const [minPlayers, setMinPlayers] = useState(Infinity);
  const [host, setHost] = useState(false);
  const { socket } = useSocketContext();
  const [previousPlayers, setPreviousPlayers] = useState([]);

  // variables para manejar local storage
  const location = useLocation();
  const url = location.pathname;
  /*
  window.performance.getEntriesByType("navigation") method returns an array of PerformanceNavigationTiming entries, which includes the type of page load
    . "navigate": TYPE_NAVIGATE (Basic navigation)
    . "reload": TYPE_RELOAD
    . "back_forward": TYPE_BACK_FORWARD
    . "prerender": TYPE_PRERENDER
  */
  let navigationType = window.performance.getEntriesByType("navigation")[0].type;


  const fetchPlayersInfo = async () => {
    try {
      const fetchedPlayers = await getPlayers(gameId);
      setPlayers(fetchedPlayers);

      const isHost = fetchedPlayers.some(player => player.host && player.id === playerId);

      if (isHost) {
        // verifo que jugadores entraron
        const newPlayers = fetchedPlayers.filter(
          newPlayer => !previousPlayers.some(prevPlayer => prevPlayer.id === newPlayer.id)
        );

        console.log('new players');
        console.log(newPlayers);
        // verifo que jugadores salieron
        const leftPlayers = previousPlayers.filter(
          prevPlayer => !fetchedPlayers.some(newPlayer => newPlayer.id === prevPlayer.id)
        );
        console.log('left players');
        console.log(leftPlayers);
        // envio mensajes por socket
        newPlayers.forEach(newPlayer => {
          if (socket) {
            socket.send(JSON.stringify({
              type: `${gameId}:CHAT_MESSAGE`,
              message: `${newPlayer.name} se ha unido al juego.`
            }));
          }
        });
        leftPlayers.forEach(leftPlayer => {
          if (socket) {
            socket.send(JSON.stringify({
              type: `${gameId}:CHAT_MESSAGE`,
              message: `${leftPlayer.name} se ha ido del juego.`
            }));
          }
        });

        setPreviousPlayers(fetchedPlayers);
      }
    } catch (err) {
      console.error("Error al obtener jugadores", err);
    }
  };


  useEffect(() => {
    getGameInfo(gameId).then((res) => {
      setMaxPlayers(res.max_players);
      setMinPlayers(res.min_players);
      setGameName(res.name);
      setPreviousPlayers([]);
    }).catch((err) =>
      console.error(`Error: Unable to retrieve basic game data. ${err}`)
    );

    //if (navigationType != 'reload') {
      getPlayer(gameId, playerId).then((res) => {
        setHost(res.host);
      }).catch((err) =>
        console.error(`Error: Unable to retrieve player data. ${err}`)
      );
    //}

    fetchPlayersInfo(); // Initial fetch
  }, [location.pathname]);

  useEffect(() => {
    // Check if the button should be active
    if (players.length >= minPlayers && host) {
      setIniciateActive(true);
    } else {
      setIniciateActive(false);
    }
  }, [players, host, minPlayers]);


  // local storage -> seteo y obtencion de data
    useEffect(() => {

      // si recargo la pagina, traigo la data de local storage
      if (navigationType === 'reload') {
        const data = JSON.parse(localStorage.getItem(url));
        console.log(`local storage data ${JSON.stringify(data)}`);
        if(data){
          setPlayerId(data.playerId);
          setHost(data.host);
          setUsername(data.username);
        }
        console.log(`PLAYERS = ${JSON.stringify(players)}`)
      };

      // si estoy en la pagina, seteo la data en local storage
      if (navigationType === 'navigate' || navigationType === 'prerender') {
        const data = {
                      username: username,
                      host: host,
                     };
        localStorage.setItem(url,JSON.stringify(data));
      };
  }, [location.pathname, username, playerId, host, players]);


  useLobbySocket(gameId, fetchPlayersInfo, host); // Subscribe to events for dynamic updates

  return (
    <div className="flex flex-col w-full h-full items-center justify-center min-h-screen bg-zinc-950 text-white p-2 md:p-4">
      <h1 className="w-full text-6xl md:text-6l text-center mb-6 md:mb-10 text-white md:text-8xl">{gameName}</h1>
      <div className="w-full mb-2 md:mb-4 text-base md:text-4xl">
        {players.length >= minPlayers ? (
          <p className="text-center text-green-400">Todo listo para empezar!</p>
        ) : (
          <p className="text-center text-gray-400">
            Deben entrar por lo menos {minPlayers} jugadores para empezar
          </p>
        )}
      </div>

      {/* Lista de jugadores y chat */}
      <div className="max-w-4xl w-full p-2 md:p-4 rounded-lg shadow-lg flex flex-col md:flex-row items-stretch space-y-2 md:space-y-0 md:space-x-4">
        <div className="w-full md:w-1/2 bg-zinc-800 p-2 md:p-4 rounded-lg">
          <PlayersList players={players} minPlayers={minPlayers} maxPlayers={maxPlayers} />
        </div>
        <div className="w-full md:w-1/1 bg-zinc-800 p-1 md:pl-6 md:p-2 rounded-lg">
          <Chat gameId={gameId} lobby={true} />
        </div>
      </div>

      {/* Botones de abandonar y empezar */}
      <div className="flex w-full justify-evenly mt-2 md:m-8 space-x-2 md:space-x-3 text-sm md:text-base">
        <BotonAbandonar gameId={gameId} />
        {host && (
          <StartButton
            gameId={gameId}
            isActive={iniciateActive}
          />
        )}
      </div>
    </div>
  );
}
