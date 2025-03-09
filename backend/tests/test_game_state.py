import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from gameState.game_state_repository import GameStateRepository
from player.player_repository import PlayerRepository
from game.game_repository import GameRepository
from board.board_repository import BoardRepository
from figureCards.figure_cards_repository import FigureCardsRepository
from movementCards.movement_cards_repository import MovementCardsRepository

from player.player_logic import PlayerLogic, get_player_logic
from figureCards.figure_cards_logic import FigureCardsLogic, get_fig_cards_logic
from movementCards.movement_cards_logic import MovementCardLogic, get_mov_cards_logic

from board.board_logic import BoardLogic, get_board_logic

from partial_movement.partial_movement_logic import PartialMovementLogic, get_partial_movement_logic

from gameState.models import StateEnum, GameState
from gameState.schemas import GameStateCreate
from player.schemas import turnEnum, PlayerInDB
from movementCards.schemas import MovementCardSchema, typeEnum

from database.db import get_db
from main import app 


client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_player_logic():
    return MagicMock(spec=PlayerLogic)

@pytest.fixture
def mock_movement_cards_logic():
    return MagicMock(spec=MovementCardLogic)


@pytest.fixture
def mock_figure_cards_logic():
    return MagicMock(spec=FigureCardsLogic)

@pytest.fixture
def mock_board_logic():
    return MagicMock(spec=BoardLogic)

@pytest.fixture
def mock_player_repo():
    return MagicMock(spec=PlayerRepository)

@pytest.fixture
def mock_game_state_repo():
    return MagicMock(spec=GameStateRepository)

@pytest.fixture
def mock_game_repo():
    return MagicMock(spec=GameRepository)

@pytest.fixture
def mock_board_repo():
    return MagicMock(spec=BoardRepository)

@pytest.fixture
def mock_fig_card_repo():
    return MagicMock(spec=FigureCardsRepository)

@pytest.fixture
def mock_mov_card_repo():
    return MagicMock(spec=MovementCardsRepository)

@pytest.fixture
def mock_partial_movement_logic():
    return MagicMock(spec=PartialMovementLogic)


@pytest.fixture
def mock_game_state():
    return MagicMock(spec=GameState)

# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_mov_card_repo, mock_fig_card_repo, mock_player_repo, mock_board_repo, 
                              mock_game_repo, mock_figure_cards_logic, mock_game_state_repo, mock_movement_cards_logic, 
                              mock_player_logic,mock_board_logic, mock_partial_movement_logic, mock_game_state, mock_db):
    def override_get_db():
        return mock_db
    
    def override_get_players_logic():
        return mock_player_logic
    
    def override_get_mov_cards_logic():
        return mock_movement_cards_logic
    
    def override_get_fig_cards_logic():
        return mock_figure_cards_logic
    
    def override_get_board_logic():
        return mock_board_logic
    
    def override_get_partial_movement_logic():
        return mock_partial_movement_logic
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[GameStateRepository] = lambda: mock_game_state_repo
    app.dependency_overrides[GameRepository] = lambda: mock_game_repo
    app.dependency_overrides[PlayerRepository] = lambda: mock_player_repo
    app.dependency_overrides[BoardRepository] = lambda: mock_board_repo
    app.dependency_overrides[FigureCardsRepository] = lambda: mock_fig_card_repo
    app.dependency_overrides[MovementCardsRepository] = lambda: mock_mov_card_repo
    app.dependency_overrides[BoardLogic] = lambda: mock_board_logic
    app.dependency_overrides[PartialMovementLogic] = lambda: mock_partial_movement_logic
    app.dependency_overrides[GameState] = lambda: mock_game_state

    
    app.dependency_overrides[get_fig_cards_logic] = override_get_fig_cards_logic
    app.dependency_overrides[get_mov_cards_logic] = override_get_mov_cards_logic
    app.dependency_overrides[get_player_logic] = override_get_players_logic
    app.dependency_overrides[get_board_logic] = override_get_board_logic
    app.dependency_overrides[get_partial_movement_logic] = override_get_partial_movement_logic

    
    yield
    app.dependency_overrides = {}  # Clean up overrides after test


@patch('figureCards.figure_cards_logic.random.shuffle')
@patch('figureCards.figure_cards_logic.random.sample')
@patch('movementCards.movement_cards_logic.random.shuffle')
@patch('movementCards.movement_cards_logic.random.sample')
@patch('player.player_logic.random.sample')
def test_game_start(mock_player_random_sample, mock_mov_random_sample, mock_mov_random_shuffle,mock_fig_random_sample, mock_fig_random_shuffle,
                    mock_board_repo, mock_game_state_repo, mock_player_repo, mock_fig_card_repo,mock_mov_card_repo, mock_game_repo, 
                    mock_figure_cards_logic, mock_movement_cards_logic, mock_player_logic, mock_board_logic, mock_db
                    ):
    game_id = 3
    game_state_id = 3
    players = [
        PlayerInDB(id=1, name="Player1", turn= turnEnum.PRIMERO, game_id= game_id, game_state_id= game_state_id ,host= True , winner= False),
        PlayerInDB(id=2, name="Player2", turn= turnEnum.PRIMERO,game_id= game_id, game_state_id= game_state_id ,host= False , winner= False )
    ]
    
    mock_player_repo.get_players_in_game.return_value = players
    
    mock_player_random_sample.return_value = [1, 2]
    mock_player_logic.assign_random_turns.return_value = players[0].id
    
    mock_movement_cards_logic.mov_card_repo = mock_mov_card_repo
    
    mock_board_logic.configure_board.return_value = {"message": "Board created successfully"}
    mock_movement_cards_logic.create_mov_deck.return_value = {"message": "Movement deck created and assigned to players"}
    mock_figure_cards_logic.create_fig_deck.return_value = {"message": "Figure deck created"}
    
    mock_game_state_repo.update_game_state.return_value = None
    mock_game_state_repo.update_current_player.return_value = None
    
    mock_fig_random_shuffle.side_effect = lambda x: x 
    mock_fig_random_sample.side_effect = lambda x, y: x[:y]
    
    
    mock_movement_cards_logic.mov_card_repo.get_movement_deck.return_value = [
    MovementCardSchema(id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=None, game_id=game_id),
    MovementCardSchema(id=2, type=typeEnum.EN_L_DER, description="test", used=False, player_id=None, game_id=game_id),
    MovementCardSchema(id=3, type=typeEnum.LINEAL_CONT, description="test", used=False, player_id=None, game_id=game_id)]
    
    mock_mov_random_shuffle.side_effect = lambda x: x
    mock_mov_random_sample.return_value = [MovementCardSchema(id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=1, game_id=1), 
        MovementCardSchema(id=2, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=game_id),
        MovementCardSchema(id=3, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=game_id)]

    with client.websocket_connect("/ws") as websocket:

        response = client.patch(
            f"game_state/start/{game_id}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Game status updated, you are playing!"}
        
        game_state_update = websocket.receive_json()
        assert game_state_update["type"] == f"GAMES_LIST_UPDATE"
        
        mock_player_repo.get_players_in_game.assert_called_with(game_id, mock_db)
        
        mock_figure_cards_logic.create_fig_deck.assert_called_once_with(mock_db, game_id)
        mock_movement_cards_logic.create_mov_deck.assert_called_once_with(game_id, mock_db)
        mock_player_logic.assign_random_turns.assert_called_once_with(players, mock_db)
        
        mock_game_state_repo.update_game_state.assert_called_once_with(game_id, StateEnum.PLAYING, mock_db)
        mock_game_state_repo.update_current_player.assert_called_once_with(game_id, players[0].id, mock_db)
        
        
def test_finish_turn(mock_game_state_repo, mock_fig_card_repo, mock_mov_card_repo, mock_partial_movement_logic, mock_db):
    game_id = 2
    next_player_id = 3
    current_player_id = 7
    movements_to_erase = False
    
    mock_game_state_repo.get_current_player.return_value = {"current_player_id": current_player_id}
    mock_game_state_repo.get_next_player_id.return_value = next_player_id
    
    mock_game_state_repo.update_current_player.return_value = None
    
    mock_fig_card_repo.grab_figure_cards.return_value = None
    mock_mov_card_repo.grab_mov_cards.return_value = None
    mock_partial_movement_logic.revert_partial_movements.return_value = movements_to_erase

    with client.websocket_connect("/ws") as websocket:

        response = client.patch(
            f"game_state/{game_id}/finish_turn"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Current player successfully updated", "reverted_movements": movements_to_erase}
        
        game_state_update = websocket.receive_json()
        assert game_state_update["type"] == f"{game_id}:NEXT_TURN"
        
        mock_game_state_repo.get_current_player.called_once_with(game_id, mock_db)
        mock_game_state_repo.get_next_player_id.called_once_with(game_id, mock_db)
        mock_game_state_repo.update_current_player.called_once_with(game_id, next_player_id, mock_db)
        mock_fig_card_repo.grab_figure_cards.called_once_with(current_player_id, game_id, mock_db)
        mock_mov_card_repo.grab_mov_cards.called_once_with(current_player_id, game_id, mock_db)
        mock_partial_movement_logic.revert_partial_movements.assert_called_once_with(game_id, current_player_id, mock_db)


def test_get_current_player(mock_game_state_repo, mock_db):
    game_id = 2
    current_player_id = 7
    
    mock_game_state_repo.get_current_player.return_value = {"current_player_id": current_player_id}

    response = client.get("/game_state/2/current_turn")

    assert response.status_code == 200
    mock_game_state_repo.get_current_player.called_once_with(game_id, mock_db)


def test_get_game_state_by_id(mock_game_state_repo, mock_db):
    game_id = 1
    current_player_id = 1
    game_state = GameStateCreate(id=1, state= StateEnum.WAITING, game_id = game_id, current_player=current_player_id)
    mock_game_state_repo.get_game_state_by_id.return_value = game_state
    
    response = client.get(f"/game_state/{game_id}")
    
    assert response.status_code == 200
    assert response.json() == game_state.model_dump()
    mock_game_state_repo.get_game_state_by_id.assert_called_once_with(game_id, mock_db)
