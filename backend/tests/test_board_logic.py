from fastapi import HTTPException, status
import pytest
from unittest.mock import MagicMock
from board.board_logic import BoardLogic
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def board_logic():
    mock_board_repo = MagicMock()
    return BoardLogic(board_repo=mock_board_repo)

def test_configure_board(board_logic, mock_db):
    game_id = 1
    
    board_logic.board_repo.get_existing_board.return_value = None
    
    mock_board = MagicMock(id=32)
    board_logic.board_repo.create_new_board.return_value = mock_board
    
    result = board_logic.configure_board(game_id=game_id, db= mock_db)
    
    board_logic.board_repo.get_existing_board.assert_called_once_with(game_id, mock_db)
    board_logic.board_repo.create_new_board.assert_called_once_with(game_id, mock_db)
    
    assert board_logic.board_repo.add_box_to_board.call_count == 36
    assert result == {"message": "Board created successfully"}

def test_configure_board_already_exists(board_logic, mock_db):
    game_id = 1
    
    board_logic.board_repo.get_existing_board.return_value = MagicMock()
    
    with pytest.raises(HTTPException) as exc_info:
        board_logic.configure_board(game_id, mock_db)
        
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == 'Board already exists'
