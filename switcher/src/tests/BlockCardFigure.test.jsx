import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import BlockCardFigureButton from "@/components/ui/BlockCardFigureButton";
import { vi } from "vitest";
import { useGameContext } from "@/context/GameContext";
import { useSocketContext } from "@/context/SocketContext";
import { blockCardFigure } from "@/services/services";

// Mock del contexto y servicios necesarios
vi.mock("@/context/GameContext", () => ({
  useGameContext: vi.fn(),
}));

vi.mock("@/context/SocketContext", () => ({
  useSocketContext: vi.fn(),
}));

vi.mock("@/services/services", () => ({
  blockCardFigure: vi.fn(),
}));

describe("BlockCardFigureButton", () => {
  const mockResetBlock = vi.fn();
  const mockSocketSend = vi.fn();

  beforeEach(() => {
    // Reseteamos los mocks antes de cada prueba
    vi.clearAllMocks();
    useGameContext.mockReturnValue({
      playerId: "123",
      currentTurn: "123",
      username: "TestUser",
    });
    useSocketContext.mockReturnValue({
      socket: { send: mockSocketSend },
    });
  });

  it("debe habilitar el botón si el jugador está en turno y tiene una carta seleccionada", () => {
    render(
      <BlockCardFigureButton
        gameId="game1"
        playerIdBlock="123" // Agregamos playerIdBlock aquí
        cardId="card1"
        figure={[1, 2, 3]}
        resetBlock={mockResetBlock}
      />
    );
    const button = screen.getByTestId("claimButtonTestId");
    expect(button).not.toBeDisabled();
  });

  it("debe deshabilitar el botón si no hay carta o el jugador no está en turno", () => {
    useGameContext.mockReturnValueOnce({
      playerId: "123",
      currentTurn: "456", // No es el turno del jugador
      username: "TestUser",
    });

    render(
      <BlockCardFigureButton
        gameId="game1"
        playerIdBlock="123"
        cardId={null}
        figure={[1, 2, 3]}
        resetBlock={mockResetBlock}
      />
    );
    const button = screen.getByTestId("claimButtonTestId");
    expect(button).toBeDisabled();
  });

  it("debe mostrar un tooltip al pasar el ratón sobre el botón", async () => {
    render(
      <BlockCardFigureButton
        gameId="game1"
        playerIdBlock="123"
        cardId="card1"
        figure={[1, 2, 3]}
        resetBlock={mockResetBlock}
      />
    );
    const button = screen.getByTestId("claimButtonTestId");
    fireEvent.mouseEnter(button);

    await waitFor(() => {
      expect(screen.getByText("Bloquear Carta")).toBeInTheDocument();
    });

    fireEvent.mouseLeave(button);
    await waitFor(() => {
      expect(screen.queryByText("Bloquear Carta")).not.toBeInTheDocument();
    });
  });

  it("debe enviar mensaje a través de socket y llamar a resetBlock en un bloqueo exitoso", async () => {
    blockCardFigure.mockResolvedValueOnce({ message: "success" });

    render(
      <BlockCardFigureButton
        gameId="game1"
        playerId="123"
        playerIdBlock="123"
        cardId="card1"
        figure={[1, 2, 3]}
        resetBlock={mockResetBlock}
      />
    );

    const button = screen.getByTestId("claimButtonTestId");
    fireEvent.click(button);

    await waitFor(() => {
      expect(blockCardFigure).toHaveBeenCalledWith("game1", "123", "123", "card1", [1, 2, 3]);
      expect(mockSocketSend).toHaveBeenCalledWith(
        JSON.stringify({
          type: "game1:CHAT_MESSAGE",
          message: "TestUser bloqueo una carta de figura.",
        })
      );
      expect(mockResetBlock).toHaveBeenCalled();
    });
  });

  it("debe mostrar un mensaje de error en caso de error en blockCardFigure", async () => {
    blockCardFigure.mockRejectedValueOnce(new Error("Error en el bloqueo"));

    render(
      <BlockCardFigureButton
        gameId="game1"
        playerIdBlock="123" // Agregamos playerIdBlock aquí
        cardId="card1"
        figure={[1, 2, 3]}
        resetBlock={mockResetBlock}
      />
    );

    const button = screen.getByTestId("claimButtonTestId");
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Error en el bloqueo")).toBeInTheDocument();
    });
  });
});
