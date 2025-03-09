// StartButton.test.jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';
import StartButton from '../components/ui/activeButton';
import { startGame } from '../services/services'; 
import { useNavigate } from 'react-router-dom';

vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(),
}));

vi.mock('../services/services', () => ({
  startGame: vi.fn(),
}));


describe('StartButton Component', () => {
  it('renders children correctly', () => {
    render(<StartButton isActive={true}>Comenzar partida</StartButton>);
    expect(screen.getByText('Comenzar partida')).toBeInTheDocument();
  });

  it('is disabled when isActive is false', () => {
    render(<StartButton isActive={false}>Comenzar partida</StartButton>);
    const StartButtonElement = screen.getByText('Comenzar partida');
    expect(StartButtonElement).toBeDisabled();
  });

  it('is enabled when isActive is true', () => {
    render(<StartButton isActive={true}>Comenzar partida</StartButton>);
    const StartButtonElement = screen.getByText('Comenzar partida');
    expect(StartButtonElement).not.toBeDisabled();
  });

  it('calls onClick when active and clicked', () => {
    const handleClick = vi.fn(); 
    render(<StartButton isActive={true} onClick={handleClick}>Comenzar partida</StartButton>);

    const StartButtonElement = screen.getByText('Comenzar partida');
    fireEvent.click(StartButtonElement);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when inactive and clicked', () => {
    const handleClick = vi.fn();
    render(<StartButton isActive={false} onClick={handleClick}>Comenzar partida</StartButton>);

    const StartButtonElement = screen.getByText('Comenzar partida');
    fireEvent.click(StartButtonElement);

    expect(handleClick).not.toHaveBeenCalled();
  });


  it('navigates to the correct path on successful startGame', async () => {
    const navigate = vi.fn();
    const gameId = '123'; 

    const startGameMock = startGame.mockResolvedValue(); 
    useNavigate.mockReturnValue(navigate);

    render(
      <StartButton isActive={true} onClick={async () => {
        await startGame(gameId);
        navigate(`/games/ongoing/${gameId}`);
      }}>
        Comenzar partida
      </StartButton>
    );

    fireEvent.click(screen.getByText('Comenzar partida'));

    await waitFor(() => {
      expect(startGameMock).toHaveBeenCalledWith(gameId);
    });

    await waitFor(() => {
      expect(navigate).toHaveBeenCalledWith(`/games/ongoing/${gameId}`);
    });
  });

  it('does not navigate on failed startGame', async () => {
    const gameId = '123'; 
    const navigate = vi.fn(); 
    const startGameError = new Error('Failed to start game');

    startGame.mockRejectedValue(startGameError);
    useNavigate.mockReturnValue(navigate);


    render(<StartButton gameId={gameId}>Comenzar partida</StartButton>); 

    fireEvent.click(screen.getByText('Comenzar partida')); 

    await new Promise((r) => setTimeout(r, 0));

    expect(startGame).toHaveBeenCalledWith(gameId);
    expect(navigate).not.toHaveBeenCalled();
  });
});
