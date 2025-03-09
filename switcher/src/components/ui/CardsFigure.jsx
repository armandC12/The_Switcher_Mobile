import React, { useEffect, useState} from 'react'
import { cn } from "@/lib/utils"
import { cardImg } from '../utils/getCardImg'
import { getDeckFigure } from '@/services/services'
import { AnimatedGroup } from './animated-group'
import { useFigureCardsSocket } from "../hooks/use-figure_cards-socket";
import { useBlockCardsFigureSocket } from "../hooks/use-block_cards_figure-socket";
import { useGameContext } from "@/context/GameContext";

export default function CardsFigure({gameId, panelOwner, setSelectedCardFigure, selectedCardFigure, name, resetMovement, selectedBlockCard, setSelectedBlockCard, resetFigureSelection, resetBlock,  playerId, getTurnInfo, currentTurn, turnBorder}) {

  // const { currentTurn } = useGameContext();
  const [loading, setLoading] = useState(true)
  const [figureCards, setFigureCards] = useState([])
  const [error, setError] = useState(null);

  const handleSelectedFigure = (figure) => {
    setSelectedCardFigure(figure);
    resetMovement();
    resetBlock();
  }

  // Maneja la selección de una carta para bloquear
  const handleBlockCardFigure = (figure) => {
    setSelectedBlockCard(figure);
    resetMovement();
    resetFigureSelection();
  }

  const fetchFigureCards = async () => {
    const figureCardsOwnerId = panelOwner === playerId ? playerId : panelOwner; 
    try {
      const cards = await getDeckFigure(gameId, figureCardsOwnerId)
      
      setFigureCards(cards)
    } catch (error) {
      setError(`Error al obtener las cartas de figura del player: ${playerId}`);
      console.error('Error fetching figure cards', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFigureCards();
  }, []);

  useFigureCardsSocket(gameId, fetchFigureCards, getTurnInfo);
  useBlockCardsFigureSocket(gameId, fetchFigureCards, getTurnInfo);

  if (loading) return <div data-testid='loadingDiv' className='m-auto align-middle'>Cargando cartas de movimiento...</div>;
  if (error) return <div className='w-full h-full mt-10 text-center'>{error}</div>;

  return (
    <div className={`flex flex-col mt-3 justify-center items-center w-full h-full mb-10`}>
      {name && <span className="text-xl text-center mb-4 sm:mb-2">{name}</span>}
      {/* <AnimatedGroup
        className="flex justify-center items-center space-x-5 w-full"
        preset="scale"
      > */}
      <AnimatedGroup
        className="flex justify-center items-center mb-0 sm:mb-0 space-x-0 sm:space-x-8 w-full sm:h-full sm,md:flex-wrap"
        preset="scale"
      >
        {figureCards.slice(0, 3).map((card) => {
          const isSelected = selectedCardFigure && selectedCardFigure.id === card.id;
          const isBlocked = selectedBlockCard && selectedBlockCard.id === card.id;

          return (
            <button
              key={card.id}
              className={cn(
                "relative sm:size-32 aspect-square rounded-lg overflow-hidden transition-transform",
                isSelected ? "scale-125" : "hover:scale-110",
                isBlocked ? "scale-125" : "hover:scale-110",
                !card.show ? "opacity-100" : "",
                !card.blocked ? "opacity-100" : "opacity-50"
              )}
              // onClick={() => handleSelectedFigure(card)}
              style={{ cursor: playerId === currentTurn? 'pointer' : 'not-allowed', opacity: playerId === currentTurn ? 1 : 0.5 }}

              onClick={() =>
                !card.blocked && card.player_id === currentTurn ? handleSelectedFigure(card): handleBlockCardFigure(card)}
                disabled={card.blocked}
            >
            {!card.show ? 
              <img data-testid='showCard'
              src={cardImg("DORSO_FIG")}
              alt={`Dorso de carta de movimiento`}
              className="absolute inset-0 opacity-100 flex items-center justify-center"
              // className={cn("object-contain w-full h-full", !card.show && "opacity-50")}
              />
              : 
              <img data-testid='figureCard'
              src={cardImg(card.type)}
              alt={`Figure card ${card.type}`}
              className={cn("object-contain w-full h-full", !card.show && "opacity-0")}
              />
            }
            {/* Capa de bloqueo */}
            {card.blocked && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                  <span className="text-white text-6xl">🔒</span>
                </div>
              )}
            </button>
          ) 
        })}
      </AnimatedGroup>
    </div>
  )
}
