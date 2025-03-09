import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from partial_movement.partial_movement_logic import PartialMovementLogic, get_partial_movement_logic
from board.schemas import BoardPosition
from board.board_repository import BoardRepository
from partial_movement.partial_movement_repository import PartialMovementRepository
from movementCards.movement_cards_repository import MovementCardsRepository

@pytest.fixture
def mock_board_repo():
    return MagicMock(spec=BoardRepository)

@pytest.fixture
def mock_partial_repo():
    return MagicMock(spec=PartialMovementRepository)

@pytest.fixture
def mock_mov_card_repo():
    return MagicMock(spec=MovementCardsRepository)

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def partial_movement_logic(mock_board_repo, mock_partial_repo, mock_mov_card_repo):
    return PartialMovementLogic(mock_board_repo, mock_partial_repo, mock_mov_card_repo)

def test_revert_partial_movements_no_movements(partial_movement_logic, mock_partial_repo, mock_db_session):
    mock_partial_repo.return_partial_movements_by_player.return_value = []
    
    result = partial_movement_logic.revert_partial_movements(game_id=1, player_id=1, db=mock_db_session)
    
    assert result == False
    mock_partial_repo.return_partial_movements_by_player.assert_called_once_with(1, 1, mock_db_session)

def test_revert_partial_movements_success(partial_movement_logic, mock_partial_repo, mock_board_repo, mock_mov_card_repo, mock_db_session):
    mock_partial_repo.return_partial_movements_by_player.return_value = [
        MagicMock(id=1, pos_from_x=0, pos_from_y=0, pos_to_x=1, pos_to_y=1, mov_card_id=1),
        MagicMock(id=2, pos_from_x=1, pos_from_y=1, pos_to_x=2, pos_to_y=2, mov_card_id=2)
    ]
    
    result = partial_movement_logic.revert_partial_movements(game_id=1, player_id=1, db=mock_db_session)
    
    assert result == True
    assert mock_board_repo.switch_boxes.call_count == 2
    assert mock_mov_card_repo.mark_card_in_player_hand.call_count == 2
    assert mock_partial_repo.undo_movement_by_id.call_count == 2
    mock_partial_repo.return_partial_movements_by_player.assert_called_once_with(1, 1, mock_db_session)