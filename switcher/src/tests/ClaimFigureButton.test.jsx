import ClaimFigureButton from "@/components/ui/claimFigureButton";
import { useGameContext } from "@/context/GameContext";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { useSocketContext } from "@/context/SocketContext";
import { claimFigure } from "@/services/services";

const mockSocketSend = vi.fn();

// Mock de servicios
vi.mock('@/services/services', () => ({
  claimFigure: vi.fn()
}));

// Mock Socket context
vi.mock('@/context/SocketContext', () => ({
  useSocketContext: () => ({
    socket: { send: mockSocketSend }
  })
}));

// Mock Game context
vi.mock('@/context/GameContext', () => {
  const original = vi.importActual('@/context/GameContext');
  return {
    ...original,
    useGameContext: vi.fn(),
  };
});

describe('Claim Figure Button', () => {
  const mockResetFigureSelection = vi.fn();
  const mockPlayerId = '1';
  const mockGameId = '5';
  const mockCardId = '10';
  const mockUsername = 'Player1';
  const mockFigure = [
    { pos_x: 0, pos_y: 2, color: "BLUE", highlighted: true },
    { pos_x: 0, pos_y: 3, color: "BLUE", highlighted: true },
    { pos_x: 0, pos_y: 4, color: "BLUE", highlighted: true },
    { pos_x: 1, pos_y: 4, color: "BLUE", highlighted: true }
  ];

  beforeEach(() => {
    useGameContext.mockReturnValue({ playerId: mockPlayerId, username: mockUsername, currentTurn: '1' });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('Should render the ClaimButton', () => {
    render(<ClaimFigureButton gameId={mockGameId} cardId={mockCardId} figure={mockFigure}/>);
    const claimButton = screen.getByTestId('claimButtonTestId');
    expect(claimButton).toBeInTheDocument();
  });

  it('should handle successful figure claim', async () => {
    claimFigure.mockResolvedValueOnce({ success: true });

    render(<ClaimFigureButton gameId={mockGameId} cardId={mockCardId} figure={mockFigure} resetFigureSelection={mockResetFigureSelection} />);
    const button = screen.getByTestId('claimButtonTestId');

    fireEvent.click(button);

    await waitFor(() => {
      expect(claimFigure).toHaveBeenCalledWith(
        mockGameId, // gameId
        mockPlayerId, // playerId
        mockCardId, // cardId
        mockFigure
      );

      expect(mockSocketSend).toHaveBeenCalledWith(
        JSON.stringify({
          type: `${mockGameId}:CHAT_MESSAGE`,
          message: `${mockUsername} reclamo una figura.`
        })
      );
      expect(mockResetFigureSelection).toHaveBeenCalled();
    });
  });

  it('Should be enabled when (figure.length!==0 && (playerId == currentTurn) && cardId)', () => {
    render(<ClaimFigureButton gameId={mockGameId} cardId={mockCardId} figure={mockFigure} />);
    const claimButton = screen.getByTestId('claimButtonTestId');
    expect(claimButton).toBeEnabled();
  });

  it('Should not be enabled when (figure.length!==0 && (playerId == currentTurn) && !cardId)', () => {
    render(<ClaimFigureButton gameId={mockGameId} figure={mockFigure} />);
    const claimButton = screen.getByTestId('claimButtonTestId');
    expect(claimButton).toBeDisabled();
  });

  it('Should be not enabled when (figure.length!==0 && !(playerId == currentTurn) && cardId)', () => {
    useGameContext.mockReturnValue({ playerId: '2', currentTurn: '1' });
    render(<ClaimFigureButton gameId={mockGameId} cardId={mockCardId} figure={mockFigure} />);
    const claimButton = screen.getByTestId('claimButtonTestId');
    expect(claimButton).toBeDisabled();
  });

  it('Should show tooltip when showTooltip', () => {
    render(<ClaimFigureButton gameId={mockGameId} cardId={mockCardId} figure={mockFigure} />);
    const claimButton = screen.getByTestId('claimButtonTestId');

    expect(screen.queryByText('Reclamar figura')).not.toBeInTheDocument();
    fireEvent.mouseEnter(claimButton);
    expect(screen.getByText('Reclamar figura')).toBeInTheDocument();
    fireEvent.mouseLeave(claimButton);
    expect(screen.queryByText('Reclamar figura')).not.toBeInTheDocument();
  });
});
