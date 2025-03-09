import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { expect, it, describe, vi } from 'vitest';
import CardsMovement from '../components/ui/CardsMovement';
import { getDeckMovement } from '@/services/services'; 


vi.mock('@/services/services', () => ({
  getDeckMovement: vi.fn(),
}));

vi.mock('@/components/hooks/used-update-cards_movement-socket', () => ({
  useUpdateCardsMovementSocket: vi.fn(),
}));

describe('CardsMovement Component', () => {
  const mockGameId = '1';
  const mockPlayer = { id: '1', name: 'Player 1' };
  const mockCards = [
    { id: '1', type: 'LINEAL_CONT', used: false },
    { id: '2', type: 'DIAGONAL_CONT', used: false },
    { id: '3', type: 'EN_L_DERECHA', used: true }, 
  ];
  const mocksetSelectedMovementCard = vi.fn();
  const mockCurrentTurn = mockPlayer.id;
  const mockResetFigureSelection = vi.fn();
  const mockResetBlock = vi.fn();

  it('renders loading state initially', async () => {
    getDeckMovement.mockImplementationOnce(() => new Promise(() => {}));

    render(
      <CardsMovement 
        gameId={mockGameId} 
        playerId={mockPlayer.id} 
        setSelectedMovementCard={mocksetSelectedMovementCard} 
        currentTurn={mockCurrentTurn}
        resetFigureSelection={mockResetFigureSelection}
        resetBlock={mockResetBlock}
      />
    );

    expect(screen.getByText('Cargando cartas de movimiento...')).toBeInTheDocument();

    getDeckMovement.mockResolvedValueOnce(mockCards);
  });

  it('renders movement cards correctly', async () => {
    getDeckMovement.mockResolvedValueOnce(mockCards);

    render(
      <CardsMovement 
        gameId={mockGameId} 
        playerId={mockPlayer.id} 
        setSelectedMovementCard={mocksetSelectedMovementCard} 
        currentTurn={mockCurrentTurn} 
        resetFigureSelection={mockResetFigureSelection}
        resetBlock={mockResetBlock}
      />
    );
    
    await waitFor(() => {
      expect(screen.getAllByTestId('notUsedMovementCardId')).toHaveLength(2); 
      expect(screen.getByTestId('UsedMovementCardId')).toBeInTheDocument(); 
    });
  });

  it('allows selecting a card if it is the current player\'s turn and the card is not used', async () => {
    getDeckMovement.mockResolvedValueOnce(mockCards);

    render(
      <CardsMovement 
        gameId={mockGameId} 
        playerId={mockPlayer.id} 
        setSelectedMovementCard={mocksetSelectedMovementCard} 
        currentTurn={mockCurrentTurn}
        resetFigureSelection={mockResetFigureSelection}
        resetBlock={mockResetBlock}
      />
    );

    await waitFor(() => {
      expect(screen.getAllByTestId('notUsedMovementCardId')).toHaveLength(2);
    });

    const firstCard = screen.getAllByTestId('notUsedMovementCardId')[0];

    fireEvent.click(firstCard);

    expect(mocksetSelectedMovementCard).toHaveBeenCalledWith(mockCards[0]);
  });

  it('does not allow selecting a card if it is not the current player\'s turn', async () => {
    const mocksetSelectedMovementCard = vi.fn();
  
    getDeckMovement.mockResolvedValueOnce(mockCards);
  
    render(
      <CardsMovement
        gameId={mockGameId}
        playerId={mockPlayer.id}
        currentTurn={'2'} 
        setSelectedMovementCard={mocksetSelectedMovementCard}
        resetFigureSelection={mockResetFigureSelection}
        resetBlock={mockResetBlock}
      />
    );
  
    await waitFor(() => {
      expect(screen.getAllByTestId('notUsedMovementCardId')).toHaveLength(2);
    });
  
    const firstCard = screen.getAllByTestId('notUsedMovementCardId')[0];
  
    fireEvent.click(firstCard);
  
    expect(mocksetSelectedMovementCard).not.toHaveBeenCalled();
  });

  it('does not allow selecting a card if it is not the current player\'s turn', async () => {
    const mocksetSelectedMovementCard = vi.fn();
  
    getDeckMovement.mockResolvedValueOnce(mockCards);
  
    render(
      <CardsMovement
        gameId={mockGameId}
        playerId={mockPlayer.id}
        currentTurn={'2'} // No es el turno del jugador
        setSelectedMovementCard={mocksetSelectedMovementCard}
        resetFigureSelection={mockResetFigureSelection}
        resetBlock={mockResetBlock}
      />
    );
  
    await waitFor(() => {
      expect(screen.getAllByTestId('notUsedMovementCardId')).toHaveLength(2);
    });
  
    const cards = screen.getAllByTestId('notUsedMovementCardId');
  
    fireEvent.click(cards[0]);
  
    expect(mocksetSelectedMovementCard).not.toHaveBeenCalled();
  });

it('displays the back of a card if it has the used property set to true', async () => {
  getDeckMovement.mockResolvedValueOnce(mockCards);

  render(
    <CardsMovement 
      gameId={mockGameId} 
      playerId={mockPlayer.id} 
      setSelectedMovementCard={mocksetSelectedMovementCard} 
      currentTurn={mockCurrentTurn}
      resetFigureSelection={mockResetFigureSelection}
      resetBlock={mockResetBlock}
    />
  );

  await waitFor(() => {
    expect(screen.getByTestId('UsedMovementCardId')).toBeInTheDocument();
  });

  const usedCard = screen.getByTestId('UsedMovementCardId');
  expect(usedCard).toHaveAttribute('alt', 'Dorso de carta de movimiento');
});

});
