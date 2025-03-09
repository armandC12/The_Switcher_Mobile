import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Depends
from main import app

from movementCards.schemas import MovementCardSchema, typeEnum
from movementCards.movement_cards_repository import MovementCardsRepository
from movementCards.movement_cards_logic import MovementCardLogic, get_mov_cards_logic

from partial_movement.partial_movement_repository import PartialMovementRepository, get_partial_movement_repository
from partial_movement.schemas import PartialMovementsBase
from board.board_repository import BoardRepository
from board.schemas import BoardPosition

from database.db import get_db
from connection_manager import manager


client = TestClient(app)


# Mock DB session
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


# Mock repository
@pytest.fixture
def mock_repo():
    return MagicMock(spec=MovementCardsRepository)

@pytest.fixture
def mock_mov_card_logic():
    return MagicMock(spec=MovementCardLogic)

@pytest.fixture
def mock_partial_movement_repo():
    return MagicMock(spec=PartialMovementRepository)

@pytest.fixture
def mock_board_repo():
    return MagicMock(spec=BoardRepository)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo,mock_mov_card_logic, mock_partial_movement_repo, mock_board_repo, mock_db):
    def override_get_db():
        return mock_db
    
    def override_get_mov_cards_logic():
        return mock_mov_card_logic
    
    def override_get_partial_movement_repository():
        return mock_partial_movement_repo
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mov_cards_logic] = override_get_mov_cards_logic

    app.dependency_overrides[MovementCardsRepository] = lambda: mock_repo
    app.dependency_overrides[PartialMovementRepository] = lambda: mock_partial_movement_repo
    app.dependency_overrides[get_partial_movement_repository] = override_get_partial_movement_repository

    app.dependency_overrides[BoardRepository] = lambda: mock_board_repo
    yield
    app.dependency_overrides = {}  # Clean up overrides after test


def test_get_players_movement_cards_success(mock_repo, mock_db):
    mock_movement_cards = [
        MovementCardSchema(id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=1, game_id=1), 
        MovementCardSchema(id=2, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=1),
        MovementCardSchema(id=3, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=1),
        MovementCardSchema(id=4, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=2, game_id=1), 
        MovementCardSchema(id=5, type=typeEnum.EN_L_DER, description="test", used=False, player_id=2, game_id=1),
        MovementCardSchema(id=6, type=typeEnum.EN_L_DER, description="test", used=False, player_id=2, game_id=1)
    ]
    
    mock_repo.get_players_movement_cards.return_value = mock_movement_cards

    response = client.get("/deck/movement/1")

    assert response.status_code == 200
    assert response.json() == [card.model_dump() for card in mock_movement_cards]
    mock_repo.get_players_movement_cards.assert_called_once_with(1, mock_db)

def test_get_players_movement_cards_not_found(mock_repo, mock_db):
    mock_repo.get_players_movement_cards.side_effect = HTTPException(
        status_code=404, 
        detail="There are no movement cards associated with this game"
    )

    response = client.get("/deck/movement/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "There are no movement cards associated with this game"}
    mock_repo.get_players_movement_cards.assert_called_once_with(1, mock_db)
    
def test_get_players_movement_cards_game_not_found(mock_repo, mock_db):
    mock_repo.get_players_movement_cards.side_effect = HTTPException(
        status_code=404, 
        detail="Game not found"
    )

    response = client.get("/deck/movement/112442")

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}
    mock_repo.get_players_movement_cards.assert_called_once_with(112442, mock_db)


def test_get_movement_cards_success(mock_repo, mock_db):
    mock_movement_cards = [
        MovementCardSchema(id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=1, game_id=1), 
        MovementCardSchema(id=2, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=1)
    ]
    mock_repo.get_movement_cards.return_value = mock_movement_cards

    response = client.get("/deck/movement/1/1")

    assert response.status_code == 200
    assert response.json() == [card.model_dump() for card in mock_movement_cards]
    mock_repo.get_movement_cards.assert_called_once_with(1, 1, mock_db)


def test_get_movement_cards_not_found(mock_repo, mock_db):
    mock_repo.get_movement_cards.side_effect = HTTPException(
        status_code=404, 
        detail="There are no movement cards associated with this game and player"
    )

    response = client.get("/deck/movement/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "There are no movement cards associated with this game and player"}
    mock_repo.get_movement_cards.assert_called_once_with(1, 1, mock_db)


def test_get_movement_card_by_id_success(mock_repo, mock_db):
    mock_movement_card = MovementCardSchema(
        id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=1, game_id=1
    )
    mock_repo.get_movement_card_by_id.return_value = mock_movement_card

    response = client.get("/deck/movement/1/1/1")

    assert response.status_code == 200
    assert response.json() == mock_movement_card.model_dump()
    mock_repo.get_movement_card_by_id.assert_called_once_with(1, 1, 1, mock_db)


def test_get_movement_card_by_id_not_found(mock_repo, mock_db):
    mock_repo.get_movement_card_by_id.side_effect = HTTPException(
        status_code=404, 
        detail="Movement card not found"
    )

    response = client.get("/deck/movement/1/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Movement card not found"}
    mock_repo.get_movement_card_by_id.assert_called_once_with(1, 1, 1, mock_db)


def test_play_movement_card(mock_repo,mock_mov_card_logic, mock_partial_movement_repo, mock_board_repo, mock_db):
    game_id = 1
    card_id = 1 
    player_id = 4
    pos_from = BoardPosition(pos=(0, 5)) 
    pos_to = BoardPosition(pos=(0, 3))
    
    mock_mov_card_logic.validate_movement.return_value = True
    
    mock_partial_movement_repo.create_partial_movement.return_value = None
    
    mock_repo.mark_card_partially_used.return_value = None
    
    mock_board_repo.switch_boxes.return_value = None
    
    with client.websocket_connect("/ws") as websocket:

        response = client.post(
            f"/deck/movement/play_card",
            json={
                "game_id": game_id,
                "card_id": card_id,
                "player_id": player_id,
                "pos_from": {"pos": [0, 5]},
                "pos_to": {"pos": [0, 3]}
            }
        )
        print(response.json())

        assert response.status_code == 201
        assert response.json() == {"message": "Great move..."}
        
        game_state_update = websocket.receive_json()
        assert game_state_update["type"] == f"{game_id}:MOVEMENT_UPDATE"
        
        mock_mov_card_logic.validate_movement.assert_called_once_with(card_id,pos_from, pos_to, mock_db)
        mock_partial_movement_repo.create_partial_movement.assert_called_once_with(game_id, player_id, card_id, pos_from, pos_to, mock_db)
        mock_repo.mark_card_partially_used.assert_called_once_with(card_id, mock_db)
        mock_board_repo.switch_boxes.assert_called_once_with(game_id, pos_from, pos_to, mock_db)
        
def test_play_movement_card_invalid_position():
    game_id = 1
    card_id = 1 
    player_id = 4
    pos_from = BoardPosition(pos=(0, 5)) 
    pos_to = BoardPosition(pos=(0, 3))
    
    response = client.post(
        f"/deck/movement/play_card",
        json={
            "game_id": game_id,
            "card_id": card_id,
            "player_id": player_id,
            "pos_from": {"pos": [0, 5]},
            "pos_to": {"pos": [2, 7]}
        }
    )
    
    assert response.status_code == 422  # Error de validacion de tipo
    assert response.json()["detail"][0]["type"] == "less_than_equal"
    assert response.json()["detail"][0]["msg"] == "Input should be less than or equal to 5"


def test_play_movement_card_invalid_move(mock_mov_card_logic, mock_partial_movement_repo, mock_board_repo, mock_db):
    game_id = 1
    card_id = 1 
    player_id = 4
    
    mock_mov_card_logic.validate_movement.return_value = False
    response = client.post(
        f"/deck/movement/play_card",
        json={
            "game_id": game_id,
            "card_id": card_id,
            "player_id": player_id,
            "pos_from": {"pos": [0, 5]},
            "pos_to": {"pos": [0, 3]}
        }
    )

    assert response.status_code == 400
    assert response.json()['detail'] == "Invalid movement"

def test_undo_movement_success(mock_partial_movement_repo, mock_board_repo, mock_repo, mock_db):
    # Mockeo un ultimo movimiento
    mock_last_movement = MagicMock()
    mock_last_movement.pos_from_x = 1
    mock_last_movement.pos_from_y = 1
    mock_last_movement.pos_to_x = 2
    mock_last_movement.pos_to_y = 2
    mock_last_movement.mov_card_id = 7
    
    game_id = 1
    player_id = 1
    
    pos_from = BoardPosition(pos=(1, 1))
    pos_to = BoardPosition(pos=(2, 2))

    
    mock_partial_movement_repo.undo_movement.return_value = mock_last_movement
    with client.websocket_connect("/ws") as websocket:
        response = client.post(f"/deck/movement/{game_id}/{player_id}/undo_move")

        assert response.status_code == 200
        assert response.json() == {"message": "The movement was undone successfully"}
        
        # Verifico que los metodos usados se llamen
        mock_partial_movement_repo.undo_movement.assert_called_once_with(game_id, player_id, mock_db)
        mock_board_repo.switch_boxes.assert_called_once_with(
            game_id, pos_from,pos_to, mock_db
        )
        mock_repo.mark_card_in_player_hand( mock_last_movement.mov_card_id, mock_db)
        
        # Verifico que se haya mandado el mensaje po ws
        movement_update = websocket.receive_json()
        assert movement_update["type"] == f"{game_id}:MOVEMENT_UPDATE"


def test_undo_movement_no_last_move(mock_partial_movement_repo, mock_board_repo, mock_db):
    mock_partial_movement_repo.undo_movement.side_effect = HTTPException(
        status_code=404,
        detail="There is no partial movement to undo"
    )
    
    game_id = 1
    player_id = 1

    response = client.post(f"/deck/movement/{game_id}/{player_id}/undo_move")

    assert response.status_code == 404
    assert response.json() == {"detail": "There is no partial movement to undo"}
    mock_partial_movement_repo.undo_movement.assert_called_once_with(game_id, player_id, mock_db)
    
