import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from player.schemas import turnEnum, PlayerCreateMatch
from game.game_repository import GameRepository
from game.endpoints import hash_password
from game.models import Game
from game.schemas import GameInDB, GameCreate
from database.db import get_db
from main import app 


client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


# Mock repository
@pytest.fixture
def mock_repo():
    return MagicMock(spec=GameRepository)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo, mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[GameRepository] = lambda: mock_repo
    yield
    app.dependency_overrides = {}  # Clean up overrides after test


def test_create_public_game_and_broadcast(mock_repo, mock_db):
    mock_game = {
        "game": {
            "name": "my game",
            "id": 1,
            "max_players": 3,
            "min_players": 3,
            "password": None,
            "is_private": False
        },
        "player": {
            "name": "PlayerOne",
            "host": True,
            "turn": turnEnum.PRIMERO
        },
        "gameState": {
            "id": 1, 
            "state": "WAITING",
            "game_id": 1
        }
    }
    mock_repo.create_game.return_value = mock_game
    
    with client.websocket_connect("/ws") as websocket:
        response = client.post(
            "/games",
            json={
                "game": mock_game["game"], "player": mock_game["player"]
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data =  response.json()
        assert response_data["game"]["name"] == "my game"
        assert response_data["game"]["password"] == None
        assert response_data["game"]["is_private"] == False
        
        game_expected = GameCreate(name="my game", max_players=3, min_players=3, password=None, is_private=False)
        player_expected = PlayerCreateMatch(name="PlayerOne", host= True, turn = turnEnum.PRIMERO)
        mock_repo.create_game.assert_called_once_with(game_expected, player_expected, mock_db)
        
        game_list_update = websocket.receive_json()
        assert game_list_update["type"] == "GAMES_LIST_UPDATE"


def test_create_private_game_and_broadcast(mock_repo, mock_db):
    mock_game = {
        "game": {
            "name": "my game",
            "id": 1,
            "max_players": 3,
            "min_players": 3,
            "password": "password",
            "is_private": True
        },
        "player": {
            "name": "PlayerOne",
            "host": True,
            "turn": turnEnum.PRIMERO
        },
        "gameState": {
            "id": 1, 
            "state": "WAITING",
            "game_id": 1
        }
    }
    mock_repo.create_game.return_value = mock_game
    
    with client.websocket_connect("/ws") as websocket:
        response = client.post(
            "/games",
            json={
                "game": mock_game["game"], "player": mock_game["player"]
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data =  response.json()
        assert response_data["game"]["name"] == "my game"
        assert response_data["game"]["password"] == "password"
        assert response_data["game"]["is_private"] == True
        
        mock_repo.create_game.assert_called_once()
        
        game_list_update = websocket.receive_json()
        assert game_list_update["type"] == "GAMES_LIST_UPDATE"


def test_get_games_success(mock_repo, mock_db):
    mock_games = [
        GameCreate(name="Test game 1", max_players=4, min_players=2, password="password", is_private=True),
        GameCreate(name="Test game 2", max_players=4, min_players=2, password=None, is_private=False)
    ]

    default_offset = 0
    default_limit = 5
    default_name = None
    default_num_players = None
    
    mock_repo.get_games.return_value = mock_games
        
    response = client.get("/games")
    
    assert response.status_code == 200
    assert response.json() == [game.model_dump() for game in mock_games]
    mock_repo.get_games.assert_called_once_with(mock_db, offset=default_offset, 
                                                limit=default_limit, name=default_name, 
                                                num_players=default_num_players
                                                )


def test_get_games_not_found(mock_repo, mock_db):
    mock_repo.get_games.side_effect = HTTPException(
        status_code=404, 
        detail="There are no games available"
    )

    default_offset = 0
    default_limit = 5
    default_name = None
    default_num_players = None
    
    response = client.get("/games")

    assert response.status_code == 404
    assert response.json() == {"detail": "There are no games available"}
    mock_repo.get_games.assert_called_once_with(mock_db, offset=default_offset, 
                                                limit=default_limit, name=default_name, 
                                                num_players=default_num_players
                                                )


def test_get_public_game_by_id_success(mock_repo, mock_db):
    mock_game = GameCreate(name="test game", max_players=4, min_players=2, password=None, is_private=False)

    mock_repo.get_game_by_id.return_value = mock_game
    
    response = client.get(f"/games/1")
    
    assert response.status_code == 200
    assert response.json() == mock_game.model_dump()
    mock_repo.get_game_by_id.assert_called_once_with(1, mock_db)


def test_get_public_game_by_id_success(mock_repo, mock_db):
    mock_game = GameCreate(name="test game", max_players=4, min_players=2, password="password", is_private=True)

    mock_repo.get_game_by_id.return_value = mock_game
    
    response = client.get(f"/games/1")
    
    assert response.status_code == 200
    assert response.json() == mock_game.model_dump()
    mock_repo.get_game_by_id.assert_called_once_with(1, mock_db)


def test_get_game_by_id_not_found(mock_repo, mock_db):
    mock_repo.get_game_by_id.side_effect = HTTPException(
        status_code = 404,
        detail = "Game not found"
    )
    
    response = client.get(f"/games/999")
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}
    mock_repo.get_game_by_id.assert_called_once_with(999, mock_db)


def test_get_game_winner(mock_repo, mock_db):
    mock_repo.get_game_winner.return_value = {
        "id": 8,
        "name": "Choa",
        "turn": turnEnum.SEGUNDO,
        "game_id": 4,
        "game_state_id": 4,
        "host": False,
        "winner": True
    }
    
    response = client.get("/games/4/winner")
    assert response.status_code == 200
    
    response_data = response.json()
    
    assert response_data["name"] == "Choa"
    assert response_data["id"] == 8
    assert response_data["winner"] 
    
    mock_repo.get_game_winner.assert_called_once_with(4,mock_db)
    
    


def test_get_game_winner_no_winner(mock_repo, mock_db):
    game_id = 7
    mock_repo.get_game_winner.side_effect = HTTPException(status_code=404, detail="There is no winner")
    
    response = client.get(f"/games/{game_id}/winner")
    
    assert response.status_code == 404
    
    response_data = response.json()
    assert response_data["detail"] == "There is no winner"
    
    mock_repo.get_game_winner.assert_called_once_with(game_id, mock_db)
    
def test_get_game_winner_not_finished(mock_repo, mock_db):
    
    game_id = 9
    mock_repo.get_game_winner.side_effect = HTTPException(status_code = 404, detail = "The game is not finished")
    
    response = client.get(f"/games/{game_id}/winner")
    
    assert response.status_code == 404
    
    response_data = response.json()
    assert response_data["detail"] == "The game is not finished"
    
    mock_repo.get_game_winner.assert_called_once_with(game_id, mock_db)