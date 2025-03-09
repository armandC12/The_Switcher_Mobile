import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, test, afterEach, expect } from 'vitest';
import CardsFigure from '../components/ui/CardsFigure';
import { getDeckFigure } from '@/services/services';

vi.mock('@/services/services', () => ({
  getDeckFigure: vi.fn(),
}));

vi.mock('@/context/SocketContext', () => ({
  useSocketContext: () => ({
    socket: {
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    },
  }),
}));

vi.mock('@/context/GameContext', () => ({
  useGameContext: () => ({
    currentTurn: '123',
  }),
}));


describe('CardsFigure', () => {
  const gameId = 'testGameId';
  const playerId = 'testPlayerId';
  const mockFigureCards = [
    {
      id: 1,
      type: "FIGE01",
      show: false,
      difficulty: "EASY",
      player_id: 1,
      game_id: 101,
    },
    {
      id: 2,
      type: "FIGE02",
      show: true,
      difficulty: "HARD",
      player_id: 1,
      game_id: 101,
    },
    {
      id: 3,
      type: "FIGE03",
      show: true,
      difficulty: "EASY",
      player_id: 1,
      game_id: 101,
    },
  ];

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('renders loading state initially', () => {
    getDeckFigure.mockReturnValue(new Promise(() => {}));

    render(<CardsFigure gameId={gameId} playerId={playerId} />);

    expect(screen.getByTestId('loadingDiv')).toBeInTheDocument();
  });


  test('does not render error message when fetching fails', async () => {

    getDeckFigure.mockRejectedValue(new Error('Error al obtener las cartas de figura'));

    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<CardsFigure gameId={gameId} playerId={playerId} />);

    await waitFor(() => {
      expect(screen.queryByText(/Error al obtener las cartas de figura/i)).not.toBeInTheDocument();
    });


    expect(consoleErrorSpy).toHaveBeenCalled();
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining('Error fetching figure cards'),
      expect.any(Error)
  );

    consoleErrorSpy.mockRestore();
  });

  test('renders figure cards when fetched successfully', async () => {
    getDeckFigure.mockResolvedValue(mockFigureCards);
  
    render(<CardsFigure gameId={gameId} playerId={playerId}/>);
  
    await waitFor(() => {
      expect(screen.queryByTestId('loadingDiv')).not.toBeInTheDocument();
    });
  
    const visibleFigureCards = screen.getAllByTestId('figureCard');
    expect(visibleFigureCards).toHaveLength(2);  
  
    const blockedCard = screen.getByTestId('showCard');
    expect(blockedCard).toBeInTheDocument();
  });
});
