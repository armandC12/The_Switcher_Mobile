import pytest
from unittest.mock import MagicMock, patch
from player.player_logic import get_player_logic
from player.models import turnEnum
from game.models import Game


@pytest.fixture
def player_logic():
    mock_player_repo = MagicMock()
    return get_player_logic(mock_player_repo)

@patch('player.player_logic.random.sample')
def test_assign_random_turns(mock_player_random_sample, player_logic):
    mock_session = MagicMock()
    
    mock_game = MagicMock(spec=Game, id=1)

    mock_player_1 = MagicMock(id=1, game_id=mock_game.id)
    mock_player_2 = MagicMock(id=2, game_id=mock_game.id)
    
    players = [mock_player_1, mock_player_2]
    
    mock_player_random_sample.return_value = [1, 2]
    
    first_player_id = player_logic.assign_random_turns(players, mock_session)

    assert first_player_id == 1

    player_logic.player_repo.assign_turn_player.assert_any_call(mock_game.id, 1, turnEnum.PRIMERO, mock_session)
    player_logic.player_repo.assign_turn_player.assert_any_call(mock_game.id, 2, turnEnum.SEGUNDO, mock_session)