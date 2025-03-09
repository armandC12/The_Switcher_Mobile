import { render, screen, waitFor, act, fireEvent } from "@testing-library/react";
import { vi, describe, beforeEach, it, expect } from "vitest";
import EndTurnButton from "@/components/ui/EndShiftButton";
import { useGameContext } from "@/context/GameContext";
import { useSocketContext } from "@/context/SocketContext";
import { pathEndTurn } from "@/services/services";

vi.mock("@/context/GameContext", () => ({
  useGameContext: vi.fn(),
}));

vi.mock("@/context/SocketContext", () => ({
  useSocketContext: vi.fn(),
}));

vi.mock("@/services/services", () => ({
  pathEndTurn: vi.fn(),
}));

describe("EndTurnButton", () => {
  const mockSocket = {
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  };

  const mockResetFigureSelection = vi.fn();
  const mockResetMovement = vi.fn(); 

  beforeEach(() => {
    vi.clearAllMocks();

    useGameContext.mockReturnValue({
      playerId: "player1",
      activeGameId: "game1",
    });

    useSocketContext.mockReturnValue({
      socket: mockSocket,
    });
  });

  it("activates the button when it's the player's turn", async () => {
    render(<EndTurnButton gameId="game1" currentTurn="player1" resetFigureSelection={mockResetFigureSelection} resetMovement={mockResetMovement} />);

    const eventData = JSON.stringify({ type: "game1:NEXT_TURN", nextPlayerId: "player1" });

    await act(async () => {
      mockSocket.addEventListener.mock.calls[0][1]({ data: eventData });
    });

    await waitFor(() => {
      expect(screen.getByTestId('endTurnButtonId')).toBeEnabled();
    });
  });

  it("disables the button when it's not the player's turn", async () => {
    render(<EndTurnButton gameId="game1" currentTurn="player2" resetFigureSelection={mockResetFigureSelection} resetMovement={mockResetMovement} />);

    const eventData = JSON.stringify({ type: "game1:NEXT_TURN", nextPlayerId: "player2" });

    await act(async () => {
      mockSocket.addEventListener.mock.calls[0][1]({ data: eventData });
    });

    await waitFor(() => {
      expect(screen.getByTestId('endTurnButtonId')).toBeDisabled();
    });
  });

  it("calls pathEndTurn and resets selections when the button is clicked", async () => {
    pathEndTurn.mockResolvedValue(true);

    render(<EndTurnButton gameId="game1" currentTurn="player1" resetFigureSelection={mockResetFigureSelection} resetMovement={mockResetMovement} />);

    await waitFor(() => {
      expect(screen.getByTestId('endTurnButtonId')).toBeEnabled();
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId('endTurnButtonId'));
    });

    expect(pathEndTurn).toHaveBeenCalledWith("game1");
    expect(mockResetFigureSelection).toHaveBeenCalled(); // Verificar que se llame a resetFigureSelection
    expect(mockResetMovement).toHaveBeenCalled(); // Verificar que se llame a resetMovement
  });
});
