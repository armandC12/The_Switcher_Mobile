import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import Winner from '../pages/Winner';
import { useGameContext } from '../context/GameContext';
import { MemoryRouter, useNavigate } from 'react-router-dom';

// Mock de imágenes
vi.mock('@/assets/logo_switcher.png', () => ({
  default: 'mocked-logo.png',
}));

vi.mock('../assets/images/fige01.svg', () => ({
  default: 'mocked-fige01.png',
}));

vi.mock('../assets/images/fige04.svg', () => ({
  default: 'mocked-fige04.png',
}));

vi.mock('../assets/images/cruceDiagonalContiguo.svg', () => ({
  default: 'mocked-cruceDiagonalContiguo.svg',
}));

vi.mock('../assets/images/cruceEnLIzquierda.svg', () => ({
  default: 'mocked-cruceEnLIzquierda.svg',
}));

vi.mock('../context/GameContext', () => ({
  useGameContext: vi.fn(),
}));

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal(); 
  return {
    ...actual, 
    useNavigate: vi.fn(), 
  };
});

describe('Winner Component', () => {
  const mockGameContext = {
    gameName: 'Game 1', 
    winnerName: 'Jugador 2', 
  };

  beforeEach(() => {
    vi.clearAllMocks();

    useGameContext.mockReturnValue(mockGameContext);
  });

  it('should render winner component correctly', () => {
    render(
      <MemoryRouter>
        <Winner />
      </MemoryRouter>
    );

    expect(screen.getByText(/Winner/i)).toBeInTheDocument();
    expect(screen.getByText(/Partida: Game 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Ganador: Jugador 2/i)).toBeInTheDocument();

    expect(screen.getByAltText('TYPE_1')).toBeInTheDocument();
    expect(screen.getByAltText('Lizquierda')).toBeInTheDocument();
    expect(screen.getByAltText('digonalContiguo')).toBeInTheDocument();
    expect(screen.getByAltText('TYPE_4')).toBeInTheDocument();
  });

  it('should navigate to /games when button is clicked', () => {
    const mockNavigate = vi.fn(); 

    useNavigate.mockReturnValue(mockNavigate);

    render(
      <MemoryRouter>
        <Winner />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /Volver al inicio/i }));

    expect(mockNavigate).toHaveBeenCalledWith('/games');
  });
});
