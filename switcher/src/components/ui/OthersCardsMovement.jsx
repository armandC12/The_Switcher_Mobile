import React, { useEffect, useState } from 'react';
import { cn } from "@/lib/utils";
import { cardImg } from '../utils/getCardImg';
import { getDeckMovement } from '@/services/services';
import { useUpdateCardsMovementSocket } from '@/components/hooks/used-update-cards_movement-socket';
import { AnimatedGroup } from './animated-group';
import { useGameContext } from "@/context/GameContext";

export default function OthersCardsMovement({ gameId, playerId }) {
    const { currentTurn } = useGameContext();
    const [movementCards, setMovementCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    useEffect(() => {
        fetchMovementCards();
    }, [gameId, playerId]);

    useUpdateCardsMovementSocket(gameId, playerId, fetchMovementCards);

    if (loading) return <div className='m-auto align-middle'>Cargando cartas de movimiento...</div>;
    if (error) return <div className='w-full h-full mt-10 text-center'>{error}</div>;

    return (
        <div className='absolute flex sm:flex-col mt-0 sm:mt-2 w-1/2 h-1/2 sm:w-full sm:h-full'>
        <AnimatedGroup
            className='w-1/2 sm:w-auto flex flex-grow sm:flex-none justify-center items-center transform translate-x-0 sm:translate-x-[-8rem] translate-y-[-13.5rem] sm:translate-y-[-15rem]'
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
            {movementCards.slice(0, 3).map((card, index) => {
                return (
                    <div
                    key={card.id}
                    className={cn(
                        "relative h-8 sm:h-14 w-auto rounded-lg overflow-hidden transform",
                        index === 0 ? '-rotate-0 translate-x-[-2rem] translate-y-[-2rem] z-30' :
                        index === 1 ? 'rotate-0 translate-x-[-2rem] translate-y-[-2rem] z-20' :
                        'rotate-0 translate-x-[-2rem] translate-y-[-2rem] z-10'
                    )}
                >
                    {card.used ? (
                        <img
                            src={cardImg("DORSO_MOV")}
                            alt={`Dorso de carta de movimiento`}
                            className="object-cover w-full h-full"
                            style={{
                                filter: 'brightness(1.2) contrast(1.3) saturate(1.5)',
                            }}
        
                        />
                    ) : (
                        // No se muestra la carta si esta usada
                        <img
                            src={cardImg("PROHIBIDO")}
                            alt={`Carta de movimiento prohibida`}
                            className="object-cover w-full h-full "
                        />
                    )}
                </div>
                )
            })}
        </AnimatedGroup>
        </div>
    );
}
