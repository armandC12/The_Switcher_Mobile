import { render, screen, waitFor } from '@testing-library/react';
import OthersCardsMovement from '@/components/ui/OthersCardsMovement';
import { vi } from 'vitest';
import { useGameContext } from "@/context/GameContext";
import { getDeckMovement } from '@/services/services';
import { useUpdateCardsMovementSocket } from '@/components/hooks/used-update-cards_movement-socket';

// Mocks
vi.mock('@/context/GameContext', () => ({
    useGameContext: vi.fn(),
}));

vi.mock('@/services/services', () => ({
    getDeckMovement: vi.fn(),
}));

vi.mock('@/components/hooks/used-update-cards_movement-socket', () => ({
    useUpdateCardsMovementSocket: vi.fn(),
}));

vi.mock('../utils/getCardImg', () => ({
    cardImg: vi.fn((type) => `/path/to/${type}.png`),
}));

// Variables de prueba
const mockGameId = 'test-game-id';
const mockPlayerId = 'test-player-id';

describe('OthersCardsMovement Component', () => {
    beforeEach(() => {
        useGameContext.mockReturnValue({ currentTurn: mockPlayerId });
    });

    // Test para verificar que se muestre el estado de carga inicialmente
    it('should display loading state initially', () => {
        getDeckMovement.mockReturnValue(new Promise(() => {})); // Deja la promesa pendiente
        render(<OthersCardsMovement gameId={mockGameId} playerId={mockPlayerId} />);
        expect(screen.getByText(/Cargando cartas de movimiento/i)).toBeInTheDocument();
    });

    // Test para verificar que se muestre un mensaje de error si falla la petición
    it('should display an error message if fetching fails', async () => {
        getDeckMovement.mockRejectedValue(new Error('Network Error'));
        render(<OthersCardsMovement gameId={mockGameId} playerId={mockPlayerId} />);
        await waitFor(() => expect(screen.getByText(/Error al obtener las cartas de movimiento/i)).toBeInTheDocument());
    });

    // Test para verificar que se rendericen las cartas correctamente cuando se obtienen exitosamente
    it('should render cards correctly when fetched successfully', async () => {
        // Mock de respuesta exitosa
        const mockCards = [
            { id: 'card-1', used: true },
            { id: 'card-2', used: false },
            { id: 'card-3', used: true },
        ];
        getDeckMovement.mockResolvedValue(mockCards);
        render(<OthersCardsMovement gameId={mockGameId} playerId={mockPlayerId} />);

        await waitFor(() => {
            expect(screen.getAllByAltText(/Dorso de carta de movimiento/i)).toHaveLength(2); // Cartas usadas
            expect(screen.getAllByAltText(/Carta de movimiento prohibida/i)).toHaveLength(1); // Carta prohibida
        });
    });

    // Test para verificar que se llame a getDeckMovement al cambiar gameId o playerId
    it('should call fetchMovementCards on gameId or playerId change', async () => {
        const { rerender } = render(<OthersCardsMovement gameId="game1" playerId="player1" />);
        expect(getDeckMovement).toHaveBeenCalledWith("game1", "player1");
        
        rerender(<OthersCardsMovement gameId="game2" playerId="player2" />);
        expect(getDeckMovement).toHaveBeenCalledWith("game2", "player2");
    });

    // Test para verificar que se actualicen las cartas usando useUpdateCardsMovementSocket
    it('should update cards using useUpdateCardsMovementSocket', () => {
        render(<OthersCardsMovement gameId={mockGameId} playerId={mockPlayerId} />);
        expect(useUpdateCardsMovementSocket).toHaveBeenCalledWith(mockGameId, mockPlayerId, expect.any(Function));
    });
});
