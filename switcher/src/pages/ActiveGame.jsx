import React, { useCallback, useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useGameContext } from '../context/GameContext';
import { getPlayers, getBoard, calculateFigures, pathEndTurn, startGame } from '@/services/services';
import { useActiveGameSocket } from '@/components/hooks/use-active_game-socket';
import { useUpdateBoardSocket } from '@/components/hooks/use-update_board-socket';
import { fetchGameState } from '@/services/services';
import { motion } from 'framer-motion';
import CardsMovement from '../components/ui/CardsMovement';
import CardsFigure from '../components/ui/CardsFigure';
import PlayerPanel from '../components/ui/PlayerPanel';
import Board from '../components/ui/GameBoard';
import { useTurnInfoSocket } from '@/components/hooks/use-turn_info-socket';
import Chat from '@/components/ui/chat';
import EndTurnButton from '@/components/ui/EndShiftButton';
import LeaveButton from '@/components/ui/LeaveButton';
import UndoButton from '@/components/ui/undoButton';
import ClaimFigureButton from '@/components/ui/claimFigureButton';
import ConfirmMovementButton from '@/components/ui/ConfirmButton';
import BlockCardFigureButton from '@/components/ui/BlockCardFigureButton';
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import { useSocketContext } from '@/context/SocketContext';


export default function ActiveGame() {
  const { gameId } = useParams();
  const { players, setPlayers, currentTurn, setCurrentTurn, username, setPlayerId, setUsername } = useGameContext();
  const {socket} = useSocketContext();
  const [boxes, setBoxes] = useState();
  const [selectedMovementCard, setSelectedMovementCard] = useState(null);
  const [selectedMovementPositions, setSelectedMovementPositions] = useState([]);
  const [blockedColor, setBlockedColor] = useState(null);
  const [selectedBoardFigure, setSelectedBoardFigure ] = useState([]);
  const [selectedCardFigure, setSelectedCardFigure] = useState(null);
  const [figuresFormed, setFiguresFormed] = useState([]);
  const [fetchedTurn, setFetchedTurn] = useState(null);
  const [loadingFig, setLoadingFig] = useState(false);
  const [loadingOut, setLoadingOut] = useState(false);
  const [syncEffect, setSyncEffect] = useState(true);
  const [previousPlayers, setPreviousPlayers] = useState(players);
  const [selectedBlockCard, setSelectedBlockCard] = useState(null);
  let {playerId} = useParams();
  playerId = Number(playerId);
  const [remainingTime, setRemainingTime] = useState(120);

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

  //const TIMER_DURATION = 120000;


  const getTurnInfo = useCallback(async () => {
    try {
      const newTurnData = await fetchGameState(gameId);
      if (newTurnData.current_player) {
        setCurrentTurn(newTurnData.current_player);
        setFetchedTurn(newTurnData.current_player); // Store fetched value

        setBlockedColor(newTurnData.forbidden_color);
      } else {
        console.error("Received an undefined player ID.");
      }
    } catch (err) {
      // console.log(err);
      throw err;
    }
  }, [setCurrentTurn, gameId]);

  const fetchPlayers = useCallback(async () => {
    try {
      const fetchedPlayers = await getPlayers(gameId);
      setPlayers(fetchedPlayers);

      const isHost = fetchedPlayers.some(player => player.host && player.id === playerId);

      if (isHost) {
        // verifo que jugadores salieron
        const leftPlayers = previousPlayers.filter(
          prevPlayer => !fetchedPlayers.some(newPlayer => newPlayer.id === prevPlayer.id)
        );
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
  }, [gameId, setPlayers, url]);

  const fetchBoard = useCallback(async () => {
    try {
      // console.log("fetchBoard ejecutado");
      const res = await getBoard(gameId);
      console.log(res);
      setBoxes(res.boxes);
      setFiguresFormed(res.formed_figures);
      setSyncEffect(true);
      // return;
    } catch (err) {
      console.error("Error fetching board:", err);
    }
  }, [gameId]);



  const resetFigureSelection = useCallback(() => {
    setSelectedBoardFigure([]);
    setSelectedCardFigure(null);
  }, [setSelectedBoardFigure, setSelectedCardFigure]);

  const resetMovement = useCallback(() => {
    setSelectedMovementCard(null);
    setSelectedMovementPositions([]);
  }, [setSelectedMovementCard, setSelectedMovementPositions]);

  const resetBlock = useCallback(() => {
    // console.log('reset cardMovementSelect:', selectedMovementCard);
    // console.log('reset cardPositionsSelect:', selectedMovementPositions);
    setSelectedBlockCard(null);
    setSelectedBoardFigure([]);
  }, [setSelectedBlockCard, setSelectedBoardFigure]);


  useEffect(() => {
    Promise.all([fetchPlayers(), fetchBoard(), getTurnInfo()]).then(() => {
      if (fetchedTurn === playerId) {
        calculateFigures(gameId); // highlight board figures
      }
    });
  }, [fetchBoard, fetchPlayers, getTurnInfo, fetchedTurn, url]);


  useEffect(() => {
    if (currentTurn !== playerId && gameId) {
      resetMovement();  // Reset if turn changes
    }
  }, [gameId, currentTurn, playerId, resetMovement]);


  const TIMER_DURATION = 120000;
  useEffect(() => {
    const timer_storage_key = `start-time-${url}`;
    let intervalId;

    //if (currentTurn === playerId) {
      let startTime;

      if (navigationType === 'reload') {
        const storedStartTime = localStorage.getItem(timer_storage_key);
        if (storedStartTime) {
          startTime = parseInt(storedStartTime, 10);
        }
      }

      if (!startTime) {
        startTime = Date.now();
        localStorage.setItem(timer_storage_key, startTime.toString());
      }

      intervalId = setInterval(() => {
        const elapsedTime = Date.now() - startTime;
        const remaining = Math.max(0, TIMER_DURATION - elapsedTime);
        setRemainingTime(remaining / 1000);


        if (remaining <= 0) {
          clearInterval(intervalId);
          localStorage.removeItem(timer_storage_key);
          if (currentTurn === playerId){
            pathEndTurn(gameId);
          }
        }
      }, 1000);

      // calculo inicial debido a que interval espera 1s para ejecutarse
      // sino lo hago, aparece al maximo, y despues de 1s se actualiza a donde verdaderamente esta
      const initialElapsedTime = Date.now() - startTime;
      const initialRemaining = Math.max(0, TIMER_DURATION - initialElapsedTime);
      setRemainingTime(initialRemaining / 1000);
    //}

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [currentTurn, playerId, url, navigationType, gameId]);

  const calculateTimeBar = useCallback((remainingTime) => {
    const percentage = (remainingTime / 120) * 100;
    return `${percentage}%`;
  }, []);

  // local storage -> seteo y obtencion de data
  useEffect(() => {

    // si recargo la pagina, traigo la data de local storage
    if (navigationType === 'reload') {
      const data = JSON.parse(localStorage.getItem(url));
      console.log(`local storage data ${JSON.stringify(data)}`);
      if(data){
        setPlayerId(data.playerId);
        setUsername(data.username);
        setCurrentTurn(data.currentTurn);
      }
    };

    // si estoy en la pagina, seteo la data en local storage
    if (navigationType === 'navigate' || navigationType === 'prerender') {
      const data = {
                    username: username,
                    playerId: playerId,
                    currentTurn: currentTurn
                   };
      localStorage.setItem(url,JSON.stringify(data));
    };
  }, [url]);

  useActiveGameSocket(gameId, fetchPlayers);
  useUpdateBoardSocket(gameId, fetchBoard, setSyncEffect, setLoadingFig);
  useTurnInfoSocket(gameId, fetchBoard, setLoadingFig, setSyncEffect);


  const otherPlayers = players.filter(p => {
    console.log(`p.id: ${JSON.stringify(p.id)}, playerID: ${JSON.stringify(playerId)}`);
    return p.id != playerId;
  });

  console.log(`player id = ${playerId}, players = ${JSON.stringify(players.map(p => p.id))}
  currentTurn = ${currentTurn}`);

  console.log("TIPOS")
  console.log(`currentTurn = ${typeof(currentTurn)}`)
  console.log(`playerId = ${typeof(playerId)}`)

  return (
    <div className="flex flex-col h-screen bg-zinc-950">

      {loadingFig && currentTurn === playerId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
          <AiOutlineLoading3Quarters className="animate-spin text-white" size={50} />
          <h2 className="text-white text-2xl ml-4">Calculando figuras formadas...</h2>
        </div>
      )}
      {loadingOut && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
          <AiOutlineLoading3Quarters className="animate-spin text-white" size={50} />
          <h2 className="text-white text-2xl ml-4">Redirigiendo...</h2>
        </div>
      )}

      {/* Other Player Panels */}
      {/* <div className="relative size-24 sm:size-32 aspect-square rounded-lg overflow-hidden transition-transform"> */}
      <div className="flex flex-row w-full text-white justify-center">
        {otherPlayers.map((player) => (
          <div key={player.id} className="relative w-1/2 sm:w-[600px] mx-13">
          {/* // <div key={player.id} className="relative w-full max-w-[600px] sm:w-[400px] sm:mx-4 mx-2"> */}
            <PlayerPanel
              game={gameId}
              panelOwner={player.id}
              playerId={playerId}
              name={player.name}
              setSelectedCardFigure={setSelectedCardFigure}
              selectedCardFigure={selectedCardFigure}
              currentTurn={currentTurn}
              getTurnInfo={getTurnInfo}
              resetMovement={resetMovement}
              selectedBlockCard={selectedBlockCard}
              setSelectedBlockCard={setSelectedBlockCard}
              resetFigureSelection={resetFigureSelection}
              resetBlock={resetBlock}
            />
            {currentTurn === player.id && (
              <div className="absolute bottom-2 sm:bottom-0 left-0 right-0 h-1 sm:h-2 overflow-hidden">
                <motion.div
                  className={`h-full bg-white`}
                  style={{
                    width: calculateTimeBar(remainingTime),
                    maxWidth: '100%'
                  }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Board and Turn Info */}
      <div className="flex flex-col sm:flex-row w-full text-white p-5 sm:p-0 justify-center gap-10 sm:gap-0">

        {/* Board */}
        {/* <div className="flex flex-col justify-around items-end mr-5 p-4 md:w-1/2">
          <div className="relative"> */}
        <div className="flex flex-col justify-around items-end mr-5 p-10 sm:p-14 w-full sm:w-1/2 mt-[-50px] sm:mt-0">
          <div className="relative w-full sm:w-auto flex justify-center">
            {boxes?
             <Board
             boxes={boxes} blockedColor={blockedColor}
             currentTurn={currentTurn} playerId={playerId}
             selectedCardFigure={selectedCardFigure}
             selectedBoardFigure={selectedBoardFigure}
             setSelectedBoardFigure={setSelectedBoardFigure}
             selectedMovementCard={selectedMovementCard}
             setSelectMovementPosition={setSelectedMovementPositions}
             selectedMovementPositions={selectedMovementPositions}
             figuresFormed={figuresFormed}
             syncEffect={syncEffect}
             selectedBlockCard={selectedBlockCard}
             />

            :<>Loading board...</>}
            {currentTurn != playerId && currentTurn && (
             <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white text-2xl">
               {`Turno de ${players.find(p => p.id === currentTurn)?.name}`}
             </div>
           )}
          </div>
        </div>

        {/* Right-side Panel: Turn Info and Your Cards */}
        <div className="sm:w-1/2 h-full flex flex-col sm:p-20 justify-center items-start sm:ml-5">
           <Chat gameId={gameId}/>
          <div className="rounded-lg bg-zinc-900 border border-zinc-800 text-white p-2.5 sm:p-6 flex flex-col sm:w-[600px] mt-[-30px] sm:mt-0 ">
            <h2 className="text-xl sm:text-4xl text-center sm:mb-10">Tus cartas</h2>
            <div className="flex flex-row sm:flex-col gap-6 sm:gap-4 w-full h-full">
              <div className="w-1/2 sm:w-full">
                <CardsMovement
                  gameId={gameId}
                  playerId={playerId}
                  setSelectedMovementCard={setSelectedMovementCard}
                  selectedMovementCard={selectedMovementCard}
                  currentTurn={currentTurn}
                  resetFigureSelection={resetFigureSelection}
                  resetBlock={resetBlock}
                  />
              </div>
              <div className="w-1/2 sm:w-full ">
                <CardsFigure
                  gameId={gameId}
                  playerId={playerId}
                  panelOwner={playerId}
                  setSelectedCardFigure={setSelectedCardFigure}
                  selectedCardFigure={selectedCardFigure}
                  resetMovement={resetMovement}
                  currentTurn={currentTurn}
                  getTurnInfo={getTurnInfo}
                  selectedBlockCard={selectedBlockCard}
                  setSelectedBlockCard={setSelectedBlockCard}
                  resetFigureSelection={resetFigureSelection}
                  resetBlock={resetBlock}
                  // turnBorder={turnBorder}
                />
              </div>
            </div>
          </div>
          {currentTurn === playerId && (
            // <div className="w-full md:w-[600px] mt-2 overflow-hidden">
            <div className="w-full max-w-[600px] mt-2 overflow-hidden">
              <motion.div
                className={`h-1 sm:h-2 z-40 ${
                  remainingTime < 15 ? 'bg-red-500' : 'bg-green-500'
                }`}
                style={{
                  width: calculateTimeBar(remainingTime),
                  maxWidth: '100%'
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          )}
        </div>
      </div>

      <motion.div
        className="fixed bottom-0 left-0 right-0 sm:left-0 sm:right-0 flex justify-around items-center bg-zinc-800 p-2 sm:p-4 z-40"
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >

        <LeaveButton gameId={gameId} setLoadingOut={setLoadingOut} />
        <ClaimFigureButton gameId={gameId} cardId={selectedCardFigure ? selectedCardFigure.id : null} figure={selectedBoardFigure} resetFigureSelection={resetFigureSelection}/>
        <UndoButton gameId={gameId} currentTurn={currentTurn} setLoadingFig={setLoadingFig} resetFigureSelection={resetFigureSelection} setSyncEffect={setSyncEffect} resetMov={resetMovement}/>
        <ConfirmMovementButton gameId={gameId} playerId={playerId} currentTurn={currentTurn}
          selectedCard={selectedMovementCard} selectedPositions={selectedMovementPositions}
          resetMov={resetMovement} setLoadingFig={setLoadingFig} setSyncEffect={setSyncEffect}// agrgue el setLoading
          />
        <BlockCardFigureButton gameId={gameId} playerIdBlock={selectedBlockCard ? selectedBlockCard.player_id : null} currentTurn={currentTurn} cardId={selectedBlockCard ? selectedBlockCard.id : null} figure={selectedBoardFigure} resetBlock={resetBlock}/>
        <EndTurnButton gameId={gameId} currentTurn={currentTurn} getTurnInfo={getTurnInfo} resetFigureSelection={resetFigureSelection} resetMovement={resetMovement} setLoadingFig={setLoadingFig}/>
      </motion.div>
    </div>
  );
}
