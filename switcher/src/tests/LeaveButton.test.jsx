import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GameProvider } from '../context/GameContext';
import LeaveButton from '../components/ui/LeaveButton';
import { createMemoryHistory } from 'history';
import { Router } from 'react-router-dom';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const gameId = 123;

vi.mock('../context/GameContext', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    GameProvider: ({ children }) => <div>{children}</div>,
    useGameContext: () => ({
      playerId: '456',
    }),
  };
});

global.fetch = vi.fn();

describe('Leave Button', () => {
  const history = createMemoryHistory();
  
  const setLoadingOut = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch.mockClear();

    render(
      <GameProvider>
        <Router location={history.location} navigator={history}>
          <LeaveButton gameId={gameId} setLoadingOut={setLoadingOut} /> 
        </Router>
      </GameProvider>
    );
  });

  it('should render', () => {
    const leaveButton = screen.getByTestId('leaveButtonId');
    expect(leaveButton).toBeTruthy();
  });

  it('post with ok data and then navigate', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reverted_movements: false }),
    });
  
    const leaveButton = screen.getByTestId('leaveButtonId');
    userEvent.click(leaveButton);
  
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/players/456/leave?game_id=123'),
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    ));
  
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/games'));
  });

});
