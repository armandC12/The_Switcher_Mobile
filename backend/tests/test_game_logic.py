import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from game.game_logic import GameLogic
from gameState.models import StateEnum
from figureCards.models import typeEnum
@pytest.fixture
def game_logic():
    mock_game_repo = MagicMock()
    mock_game_state_repo = MagicMock()
    mock_player_repo = MagicMock()
    mock_figure_cards_repo = MagicMock()
    return GameLogic(game_repository=mock_game_repo, game_state_repository=mock_game_state_repo, 
                     player_repository=mock_player_repo, figure_cards_repo=mock_figure_cards_repo)


@pytest.mark.asyncio
async def test_check_win_condition_one_player_left(game_logic):
    game_id = 1
    game_state_id = 1
    #Mock game 
    mock_game = MagicMock()
    mock_game.id = game_id
    mock_game.players = [MagicMock(id=1, name="Player1", game_id = game_id , game_state_id = game_state_id, host=True, winner = False)]
    
    #Mock session
    mock_session = MagicMock()

    game_logic.player_repo.get_players_in_game.return_value = mock_game.players
    
    #Mock handle win
    result = game_logic.check_win_condition_one_player_left(mock_game.id, mock_session)

    assert result
    
@pytest.mark.asyncio
async def test_check_win_condition_one_player_left_no_win(game_logic):
    game_id = 1
    game_state_id = 1
    #Mock game 
    mock_game = MagicMock()
    mock_game.id = game_id
    mock_game.players = [MagicMock(id=1, name="Player1", game_id = game_id , game_state_id = game_state_id, host=True, winner = False),
                         MagicMock(id=2, name="Player2", game_id = game_id , game_state_id = game_state_id, host=False, winner = False)
                         ]
    
    #Mock session
    mock_session = MagicMock()

    game_logic.player_repo.get_players_in_game.return_value = mock_game.players
    
    #Mock handle win
    result = game_logic.check_win_condition_one_player_left(mock_game.id, mock_session)

    assert not result 
        
@pytest.mark.asyncio
async def test_check_win_condition_no_figure_cards(game_logic):
    game_id = 1
    game_state_id = 1
    #Mock game 
    mock_game = MagicMock()
    mock_game.id = game_id
    mock_game.players = [MagicMock(id=1, name="Player1", game_id = game_id , game_state_id = game_state_id, host=True, winner = False)]
    
    #Jugador sin cartas
    
    #Mock session
    mock_session = MagicMock()

    game_logic.figure_cards_repo.get_figure_cards.return_value = []
    
    #Mock handle win
    result = game_logic.check_win_condition_no_figure_cards(mock_game.id, mock_game.players[0].id , mock_session)
    
    assert result
    
@pytest.mark.asyncio
async def test_check_win_condition_no_figure_cards_no_win(game_logic):
    game_id = 1
    game_state_id = 1
    #Mock game 
    mock_game = MagicMock()
    mock_game.id = game_id
    mock_game.players = [MagicMock(id=1, name="Player1", game_id = game_id , game_state_id = game_state_id, host=True, winner = False)]
    
    #Jugador sin cartas
    
    #Mock session
    mock_session = MagicMock()
    
    game_logic.figure_cards_repo.get_figure_cards.return_value = [
            MagicMock(player_id=mock_game.players[0].id, game_id=mock_game.id, show=True, type=typeEnum.FIG01),
            MagicMock(player_id=mock_game.players[0].id, game_id=mock_game.id, show=True, type=typeEnum.FIG02), 
            MagicMock(player_id=mock_game.players[0].id, game_id=mock_game.id, show=True, type=typeEnum.FIG03)
        ]
    
    #Mock handle win
    result = game_logic.check_win_condition_no_figure_cards(mock_game.id, mock_game.players[0].id , mock_session)
    
    assert not result
    
@pytest.mark.asyncio
@patch('game.game_logic.manager', new_callable=AsyncMock)
async def test_handle_win(mock_manager, game_logic):
    game_id = 1
    game_state_id = 1

    last_player = MagicMock(id=6, name="Haerin", game_id = game_id , game_state_id = game_state_id, host=True, winner = False)
    
    mock_session = MagicMock()

    game_logic.player_repo.get_player_by_id.return_value = last_player
    game_logic.game_state_repo.update_game_state.return_value = None
    game_logic.player_repo.assign_winner_of_game.return_value = None
        
    await game_logic.handle_win(game_id, last_player.id, mock_session)
    
    game_logic.game_state_repo.update_game_state.assert_called_once_with(1, StateEnum.FINISHED, mock_session)
    game_logic.player_repo.assign_winner_of_game.assert_called_once_with(game_id, last_player.id, mock_session)
    
    mock_manager.broadcast.assert_called_once_with({
        "type": "PLAYER_WINNER",
        "game_id": game_id,
        "winner_id": last_player.id,
        "winner_name": last_player.name
    })

    
    

    