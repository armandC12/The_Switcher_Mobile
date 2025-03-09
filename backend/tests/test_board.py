import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from board.board_repository import BoardRepository
from board.schemas import BoardAndBoxesOut, BoxOut, ColorEnum

from figureCards.models import typeEnum
from figureCards.figure_cards_logic import FigureCardsLogic , get_fig_cards_logic

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
    return MagicMock(spec=BoardRepository)

@pytest.fixture
def mock_fig_cards_logic():
    return MagicMock(spec=FigureCardsLogic)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo, mock_fig_cards_logic, mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[BoardRepository] = lambda: mock_repo
    app.dependency_overrides[get_fig_cards_logic] = lambda: mock_fig_cards_logic

    yield
    app.dependency_overrides = {}  # Clean up overrides after test


@pytest.mark.asyncio
async def test_get_board(mock_repo, mock_db):
    game_id = 1

    # Mock the return value of get_configured_board
    mock_board = BoardAndBoxesOut(
        game_id=game_id,
        board_id=1,
        boxes=[
            [BoxOut(id=1, color=ColorEnum.RED, pos_x=0, pos_y=0, highlighted=False, figure_id=None, figure_type=None)],
            [BoxOut(id=1, color=ColorEnum.RED, pos_x=0, pos_y=1, highlighted=True, figure_id=0, figure_type=typeEnum.FIG01)],
            [BoxOut(id=1, color=ColorEnum.RED, pos_x=0, pos_y=2, highlighted=True, figure_id=0, figure_type=typeEnum.FIG01)],
            [BoxOut(id=1, color=ColorEnum.RED, pos_x=0, pos_y=3, highlighted=True, figure_id=0, figure_type=typeEnum.FIG01)]
            ]
    )
    mock_repo.get_configured_board.return_value = mock_board

    # Mock the return value of get_figures
    mock_figures = [
        [
            {
                "color": ColorEnum.RED,
                "pos_x": 0,
                "pos_y": 1,
                "highlighted": True,
                "figure_id": 0,
                "figure_type": typeEnum.FIG01
            },
            {
                "color": ColorEnum.RED,
                "pos_x": 0,
                "pos_y": 2,
                "highlighted": True,
                "figure_id": 0,
                "figure_type": typeEnum.FIG01
            },
            {
                "color": ColorEnum.RED,
                "pos_x": 0,
                "pos_y": 3,
                "highlighted": True,
                "figure_id": 0,
                "figure_type": typeEnum.FIG01
            }
        ]
    ]
    mock_repo.get_figures.return_value = mock_figures

    # Make the request
    response = client.get(f"/board/{game_id}")

    # Assert the response
    assert response.status_code == 200
    result = response.json()
    assert result["game_id"] == game_id
    assert result["board_id"] == 1
    assert len(result["boxes"]) == 4
    assert len(result["boxes"][0]) == 1
    assert result["boxes"][0][0]["color"] == ColorEnum.RED
    assert result["boxes"][0][0]["pos_x"] == 0
    assert result["boxes"][0][0]["pos_y"] == 0
    assert result["boxes"][0][0]["highlighted"] == False
    assert result["boxes"][0][0]["figure_id"] == None
    assert result["boxes"][0][0]["figure_type"] == None
    assert len(result["formed_figures"]) == 1
    assert result["formed_figures"][0][0]["figure_id"] == 0
    assert result["formed_figures"][0][0]["figure_type"] == typeEnum.FIG01
    
@pytest.mark.asyncio
async def test_calculate_figures(mock_fig_cards_logic, mock_db):
    game_id = 1

    mock_fig_cards_logic.get_formed_figures.return_value = None

    with client.websocket_connect("/ws") as websocket:
        response = client.patch(f"/board/calculate_figures/{game_id}")

        assert response.status_code == 200
        result = response.json()
        assert result["message"] == "Figures Calculated!"

        mock_fig_cards_logic.get_formed_figures.assert_called_once_with(game_id, mock_db)

        board_update = websocket.receive_json()
        assert board_update["type"] == f"{game_id}:BOARD_UPDATE"