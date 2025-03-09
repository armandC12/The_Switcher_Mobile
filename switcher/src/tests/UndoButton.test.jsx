import UndoButton from "@/components/ui/undoButton";
import userEvent from "@testing-library/user-event";
import { useGameContext } from "@/context/GameContext";
import { useSocketContext } from "@/context/SocketContext";
import { undoMovement } from "@/services/services";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";

describe('Undo Button', () => {

    const mockGameId = '123';
    const mockPlayerId = '1';
    const mockNextPlayerId = '2';
    const mockUsername = 'Player1';

    vi.mock('@/context/GameContext', async () => {
        const original = await vi.importActual('@/context/GameContext');
        return {
            ...original,
            useGameContext: vi.fn(),
        };
    });

    vi.mock('@/context/SocketContext', async () => {
        const original = await vi.importActual('@/context/SocketContext');
        return {
            ...original,
            useSocketContext: vi.fn(),
        };
    });

    vi.mock('@/services/services', () => ({
        undoMovement: vi.fn(),
    }));

    beforeEach(() => {
        useGameContext.mockReturnValue({ playerId: mockPlayerId, username: mockUsername });

        // Mock del socket y su método send
        const mockSend = vi.fn();
        useSocketContext.mockReturnValue({ socket: { send: mockSend } });

        global.fetch = vi.fn();
    });

    afterEach(() => {
        vi.clearAllMocks();
    });


    it('Should send a socket message when undoing a movement', async () => {
        undoMovement.mockResolvedValueOnce({ ok: true });

        render(<UndoButton gameId={mockGameId} currentTurn={mockPlayerId} resetFigureSelection={vi.fn()} resetMov={vi.fn()} />);
        const undoButton = screen.getByTestId('undoButtonId');
        await userEvent.click(undoButton);

        // Verificar que undoMovement fue llamado correctamente
        await waitFor(() => expect(undoMovement).toHaveBeenCalledWith(mockGameId, mockPlayerId));

        // Verificar que socket.send fue llamado con el mensaje correcto
        const { socket } = useSocketContext();
        expect(socket.send).toHaveBeenCalledWith(JSON.stringify({
            type: `${mockGameId}:CHAT_MESSAGE`,
            message: `${mockUsername} deshizo un movimiento.`
        }));
    });

    it('Should render the UndoButton component and be enabled when it is player\'s turn', () => {
        render(<UndoButton gameId={mockGameId} currentTurn={mockPlayerId} />);
        const undoButton = screen.getByTestId('undoButtonId');
        expect(undoButton).toBeInTheDocument();
        expect(undoButton).not.toBeDisabled();
    });

    it('Should not enable the button when it is not the player\'s turn', () => {
        render(<UndoButton gameId={mockGameId} currentTurn={mockNextPlayerId} />);
        const undoButton = screen.getByTestId('undoButtonId');
        expect(undoButton).toBeDisabled();
    });

    it('Should handle null values for gameId and playerId', async () => {
        useGameContext.mockReturnValue({ playerId: null });
        render(<UndoButton gameId={null} currentTurn={null} resetFigureSelection={vi.fn()} resetMov={vi.fn()} />);

        const undoButton = screen.getByTestId('undoButtonId');
        await userEvent.click(undoButton);

        await waitFor(() => expect(undoMovement).not.toHaveBeenCalled());
        expect(await screen.findByText(/Error al deshacer movimiento: \(!gameId \|\| !playerId\)/)).toBeInTheDocument();
    });

    it('Should handle undefined values for gameId and playerId', async () => {
        useGameContext.mockReturnValue({ playerId: undefined });
        render(<UndoButton gameId={undefined} currentTurn={undefined} resetFigureSelection={vi.fn()} resetMov={vi.fn()} />);

        const undoButton = screen.getByTestId('undoButtonId');
        await userEvent.click(undoButton);

        await waitFor(() => expect(undoMovement).not.toHaveBeenCalled());
        expect(await screen.findByText(/Error al deshacer movimiento: \(!gameId \|\| !playerId\)/)).toBeInTheDocument();
    });

    it('Should show error when response is not ok', async () => {
        const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
        undoMovement.mockRejectedValueOnce(new Error('Error en la petición'));

        render(<UndoButton gameId={mockGameId} currentTurn={mockPlayerId} resetFigureSelection={vi.fn()} resetMov={vi.fn()} />);
        const mockUndoButton = screen.getByTestId('undoButtonId');

        await userEvent.click(mockUndoButton);
        await waitFor(() => expect(undoMovement).toHaveBeenCalledOnce());

        expect(consoleErrorSpy).toHaveBeenCalledWith('Error al deshacer movimiento: Error en la petición');
        expect(await screen.findByText(/Error al deshacer movimiento: Error en la petición/)).toBeInTheDocument();
    });

    it('Should show error when undoMovement throws one', async () => {
        const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
        undoMovement.mockRejectedValueOnce(new Error('Network error'));

        const resetFigureSelection = vi.fn();
        const resetMov = vi.fn();

        render(<UndoButton gameId={mockGameId} currentTurn={mockPlayerId} resetFigureSelection={resetFigureSelection} resetMov={resetMov} />);
        const undoButton = screen.getByTestId('undoButtonId');
        await userEvent.click(undoButton);

        await waitFor(() => expect(consoleErrorSpy).toHaveBeenCalledWith('Error al deshacer movimiento: Network error'));
        expect(await screen.findByText(/Error al deshacer movimiento: Network error/)).toBeInTheDocument();
    });
});

