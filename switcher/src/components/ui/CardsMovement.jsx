import React, { useEffect, useState } from 'react';
import { cn } from "@/lib/utils";
import { cardImg } from '../utils/getCardImg';
import { getDeckMovement } from '@/services/services';
import { useUpdateCardsMovementSocket } from '@/components/hooks/used-update-cards_movement-socket';
import { AnimatedGroup } from './animated-group';

// Componente que representa las cartas de movimiento
export default function CardsMovement ({ gameId, playerId, setSelectedMovementCard, selectedMovementCard, currentTurn, resetFigureSelection, resetBlock}) {

  const [movementCards, setMovementCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Obtiene las cartas de movimiento del jugador
  const fetchMovementCards = async () => {
    try {
      const cards = await getDeckMovement(gameId, playerId);
      setMovementCards(cards);
    } catch (error) {
      setError("Error al obtener las cartas de movimiento");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Obtiene las cartas de movimiento al montar el componente
  useEffect(() => {
    fetchMovementCards();
  }, [gameId, playerId, setMovementCards, setLoading]);


  const handleCardSelect = (card) => {
    if (playerId !== currentTurn || card.used) {
      return; // No permite seleccionar si no es el turno del jugador o si la carta ya está usada
    }
    console.log('CartaMovement seleccionada:', card);
    setSelectedMovementCard(card);
    resetFigureSelection();
    resetBlock();
  };

  // Escucha el socket de actualización de cartas de movimiento (card.used y undo_move)
  useUpdateCardsMovementSocket(gameId, playerId, fetchMovementCards);

  if (loading) return <div className='m-auto align-middle'>Cargando cartas de movimiento...</div>;
  if (error) return <div className='w-full h-full mt-10 text-center'>{error}</div>;

  return (
    // <div className="">
     <AnimatedGroup
      className='flex flex-row justify-center items-center h-full w-full space-x-2 sm:space-x-10'
      variants={{
        container: {
          hidden: { opacity: 0 },
          visible: {
            opacity: 1,
            transition: {
              staggerChildren: 0.05,
            },
          },
        },
        item: {
          hidden: { opacity: 0, y: 40, filter: 'blur(4px)' },
          visible: {
            opacity: 1,
            y: 0,
            filter: 'blur(0px)',
            transition: {
              duration: 1.2,
              type: 'spring',
              bounce: 0.3,
            },
          },
        },
      }}
    >
    {movementCards.map((card, index) => {
        const isSelected = selectedMovementCard && selectedMovementCard?.id === card.id;

        return (
          <button
            key={card.id}
            className={cn(
              "relative h-24 sm:h-44 w-auto rounded-lg overflow-hidden transition-transform",
              isSelected ? 'scale-125' : 'hover:scale-110',
              (index === 0 && movementCards.length !== 1) ? 'sm:-rotate-12' :
              (index === movementCards.length - 1 && movementCards.length !== 1) ? 'sm:rotate-12' : 'sm:-translate-y-5'
            )}
            onClick={() => handleCardSelect(card)}
            style={{ cursor: playerId == currentTurn ? 'pointer' : 'not-allowed', opacity: playerId == currentTurn ? 1 : 0.5 }}
          >
            {card.used ? (
              <img
              src={cardImg("DORSO_MOV")}
              alt={`Dorso de carta de movimiento`}
              data-testid="UsedMovementCardId"
              className="object-cover w-full h-full"
              />
            ) : (
              <img
                src={cardImg(card.type)}
                data-testid="notUsedMovementCardId"
                alt={`Carta de movimiento ${card.type}`}
                className="object-cover w-full h-full"
              />
            )}
          </button>
        );
      })}
    </AnimatedGroup>
  // </div>
  );
}
