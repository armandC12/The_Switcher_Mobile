import pytest
from unittest.mock import MagicMock, call, patch, AsyncMock

from sqlalchemy.orm import Session

from figureCards.figure_cards_logic import FigureCardsLogic
from figureCards.models import typeEnum, DirectionEnum, FigureCard
from figureCards.schemas import BlockFigureCardInput, PlayFigureCardInput

from game.game_logic import GameLogic
from gameState.models import GameState
from player.models import Player
from player.player_logic import PlayerLogic

from board.schemas import ColorEnum, BoxOut, BoardAndBoxesOut

from gameState.schemas import GameStateInDB, StateEnum
from fastapi import HTTPException, status

from connection_manager import ConnectionManager

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def player_repo():
    return MagicMock()

@pytest.fixture
def game_repo():
    return MagicMock()

@pytest.fixture
def game_state_repo():
    return MagicMock()

@pytest.fixture
def board_repo():
    return MagicMock()

@pytest.fixture
def fig_card_repo():
    return MagicMock()

@pytest.fixture
def mov_card_repo():
    return MagicMock()

@pytest.fixture
def partial_mov_repo():
    return MagicMock()

@pytest.fixture
def fig_cards_logic(player_repo, fig_card_repo, game_repo, game_state_repo, board_repo, mov_card_repo, partial_mov_repo):
    return FigureCardsLogic(player_repo=player_repo ,fig_card_repo=fig_card_repo, game_repo=game_repo, game_state_repo=game_state_repo, 
                            board_repo=board_repo, mov_card_repo=mov_card_repo, partial_mov_repo=partial_mov_repo)

@pytest.fixture
def mock_fig_cards_logic():
    return MagicMock(spec=FigureCardsLogic)

@pytest.fixture
def player_logic(player_repo):
    return PlayerLogic(player_repo= player_repo)

@pytest.fixture
def game_logic(game_repo, game_state_repo, player_repo, fig_card_repo):
    return GameLogic(game_repository=game_repo, game_state_repository=game_state_repo, player_repository=player_repo, figure_cards_repo=fig_card_repo)

@pytest.fixture
def mock_manager():
    return MagicMock(spec=ConnectionManager)

def test_create_fig_deck(fig_cards_logic, player_logic):
    mock_session = MagicMock()
    game_id = 1
    
    mock_player_1 = MagicMock(id=1)
    
    player_logic.player_repo.get_players_in_game.return_value = [mock_player_1]
    
    with patch('random.shuffle', lambda x: x):
        response = fig_cards_logic.create_fig_deck(mock_session, game_id)
    
    assert response == {"message": "Figure deck created"}
    
    expected_calls = [
        ((1, game_id, typeEnum.FIGE01, False, False, mock_session),),
        ((1, game_id, typeEnum.FIGE02, False, False, mock_session),),
        ((1, game_id, typeEnum.FIGE03, False, False, mock_session),),
        ((1, game_id, typeEnum.FIGE04, False, False, mock_session),),
        ((1, game_id, typeEnum.FIGE05, False, False, mock_session),),
        ((1, game_id, typeEnum.FIGE06, False, False, mock_session),),
        ((1, game_id, typeEnum.FIGE07, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG01, True, False, mock_session),),
        ((1, game_id, typeEnum.FIG02, True, False, mock_session),),
        ((1, game_id, typeEnum.FIG03, True, False, mock_session),),
        ((1, game_id, typeEnum.FIG04, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG05, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG06, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG07, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG08, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG09, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG10, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG11, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG12, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG13, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG14, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG15, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG16, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG17, False, False, mock_session),),
        ((1, game_id, typeEnum.FIG18, False, False, mock_session),)
    ]
    
    # fig_cards_logic.fig_card_repo.create_figure_card.assert_has_calls(expected_calls, any_order=True)
    # me fijo que tenga 25 llamadas
    assert fig_cards_logic.fig_card_repo.create_figure_card.call_count == len(expected_calls)
    
    calls = fig_cards_logic.fig_card_repo.create_figure_card.call_args_list

    # me fijo que solo hayan 3 cartas mostradas
    shown_cards = sum(1 for call in calls if call[0][3] is True)
    assert shown_cards == 3

    # me fijo que las funciones se llamen correctamente
    for call in calls:
        assert len(call[0]) == 6 # cada llamada tiene 5 arguments
        assert isinstance(call[0][0], int)
        assert isinstance(call[0][1], int)
        assert isinstance(call[0][2], typeEnum)
        assert isinstance(call[0][3], bool)
        assert isinstance(call[0][4], bool)

def test_create_fig_deck_no_players(fig_cards_logic, player_logic):
    mock_session = MagicMock()
    game_id = 1
        
    player_logic.player_repo.get_players_in_game.return_value = []
    
    with patch('random.shuffle', lambda x: x):
        response = fig_cards_logic.create_fig_deck(mock_session, game_id)
    
    assert response == {"message": "Figure deck was not created, there no players in game"}

def test_check_game_exists(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()
    
    fig_cards_logic.game_repo.get_game_by_id.side_effect = HTTPException(status_code=404, detail="Game not found")
    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_game_exists(game_id, mock_db)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"

def test_check_game_exists_game_found(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()
    
    fig_cards_logic.game_repo.get_game_by_id.return_value = {"id": game_id}
    result = fig_cards_logic.check_game_exists(game_id, mock_db)
    
    assert result is None

def test_check_game_in_progress_game_not_found(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    fig_cards_logic.game_state_repo.get_game_state_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_game_in_progress(game_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found when getting formed figures"

def test_check_game_in_progress_game_not_in_progress(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    mock_game_state = GameStateInDB(
        id=1,
        state=StateEnum.FINISHED,
        game_id=game_id,
        current_player=None
    )
    fig_cards_logic.game_state_repo.get_game_state_by_id.return_value = mock_game_state
    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_game_in_progress(game_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not in progress when getting formed figures"

def test_check_game_in_progress_game_playing(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    mock_game_state = GameStateInDB(
        id=1,
        state=StateEnum.PLAYING,
        game_id=game_id,
        current_player=None
    )
    fig_cards_logic.game_state_repo.get_game_state_by_id.return_value = mock_game_state
    result = fig_cards_logic.check_game_in_progress(game_id, mock_db)

    assert result is None
    
def test_get_board_or_404_board_found(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    mock_board = {
        "game_id":game_id,
        "board_id":1,
        "boxes":[]
    }
    
    fig_cards_logic.board_repo.get_configured_board.return_value = mock_board
    
    result = fig_cards_logic.get_board_or_404(game_id, mock_db)

    assert result == mock_board

def test_get_board_or_404_board_not_found(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    fig_cards_logic.board_repo.get_configured_board.side_effect = HTTPException(status_code=404, detail="Board not found")
    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.get_board_or_404(game_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Board not found"

def test_is_valid_pointer(fig_cards_logic):
    pointer_inside_bounds = (3, 4)
    pointer_outside_bounds = (6, 7)
    pointer_negative = (-1, 2)

    assert fig_cards_logic.is_valid_pointer(pointer_inside_bounds) is True

    assert fig_cards_logic.is_valid_pointer(pointer_outside_bounds) is False

    assert fig_cards_logic.is_valid_pointer(pointer_negative) is False

def test_check_surroundings_invalid_pointer(fig_cards_logic):
    figure = [{"pos_x": 1, "pos_y": 1, "color": ColorEnum.RED}]
    pointer = (1, 1)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures = []
    )
    color = ColorEnum.RED
    mock_db = MagicMock()

    fig_cards_logic.move_pointer = MagicMock(side_effect=lambda pointer, direction: (pointer[0] + 1, pointer[1]) if direction == DirectionEnum.RIGHT else (pointer[0] - 1, pointer[1]) if direction == DirectionEnum.LEFT else (pointer[0], pointer[1] + 1) if direction == DirectionEnum.DOWN else (pointer[0], pointer[1] - 1))
    fig_cards_logic.is_valid_pointer = MagicMock(side_effect=lambda pointer: False)
    fig_cards_logic.belongs_to_figure = MagicMock(side_effect=lambda pointer, figure: any(box["pos_x"] == pointer[0] and box["pos_y"] == pointer[1] for box in figure))

    result = fig_cards_logic.check_surroundings(figure, pointer, board, color, mock_db)
    assert result is True

    pointer = (-1, -1)
    result = fig_cards_logic.check_surroundings(figure, pointer, board, color, mock_db)
    assert result is False

def test_check_surroundings(fig_cards_logic):
    figure = [
        BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=1, highlighted=True),
        BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=1, highlighted=True),
        BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=True),
        BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=True)
    ]
    pointer = (1, 1)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.RED, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.RED, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.RED, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.RED, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.RED, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures = []
    )
    color = ColorEnum.BLUE
    db = MagicMock()

    result = fig_cards_logic.check_surroundings(figure, pointer, board, color, db)

    assert result is True

    board.boxes[1][1].color = ColorEnum.RED

    result = fig_cards_logic.check_surroundings(figure, pointer, board, color, db)

    assert result is False

    board.boxes[1][1].color = ColorEnum.BLUE
    board.boxes[1][0].color = ColorEnum.BLUE

    result = fig_cards_logic.check_surroundings(figure, pointer, board, color, db)

    assert result is False

def test_move_pointer(fig_cards_logic):
    initial_pointer = (2, 2)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.UP)
    assert result == (2, 1)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.DOWN)
    assert result == (2, 3)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.LEFT)
    assert result == (1, 2)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.RIGHT)
    assert result == (3, 2)

def test_belongs_to_figure(fig_cards_logic):
    figure = [
        BoxOut(id=1, color="RED", pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type="FIG01"),
        BoxOut(id=2, color="BLUE", pos_x=2, pos_y=2, highlighted=False, figure_id=1, figure_type="FIG01")
    ]
    
    pointer_inside = (1, 1)
    pointer_outside = (3, 3)

    assert fig_cards_logic.belongs_to_figure(pointer_inside, figure) is True

    assert fig_cards_logic.belongs_to_figure(pointer_outside, figure) is False

def test_check_path_blind(fig_cards_logic):
    path = [DirectionEnum.RIGHT, DirectionEnum.RIGHT, DirectionEnum.DOWN]
    pointer = (1, 1)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )
    color = ColorEnum.RED
    figure_id = 1
    figure_type = "FIGE05"
    db = MagicMock()

    result = fig_cards_logic.check_path_blind(path, pointer, board, color, figure_id, figure_type, db)

    assert result == [
        BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
        BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
        BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
        BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False)
    ]

def test_check_path_blind_invalid_path(fig_cards_logic):
    path = [DirectionEnum.RIGHT, DirectionEnum.RIGHT, DirectionEnum.UP]
    pointer = (1, 1)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )
    color = ColorEnum.RED
    figure_id = 1
    figure_type = "FIGE05"
    db = MagicMock()

    result = fig_cards_logic.check_path_blind(path, pointer, board, color, figure_id, figure_type, db)
    
    assert result is False

def test_check_path_blind_invalid_pointer(fig_cards_logic):
    path = [DirectionEnum.RIGHT, DirectionEnum.RIGHT, DirectionEnum.DOWN]
    pointer = (1, 4)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )
    color = ColorEnum.RED
    figure_id = 1
    figure_type = "FIGE05"
    db = MagicMock()

    result = fig_cards_logic.check_path_blind(path, pointer, board, color, figure_id, figure_type, db)

    assert result is False

def test_check_path_blind_invalid_color(fig_cards_logic):
    path = [DirectionEnum.RIGHT, DirectionEnum.RIGHT, DirectionEnum.DOWN]
    pointer = (1, 1)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )
    color = ColorEnum.BLUE
    figure_id = 1
    figure_type = "FIGE05"
    db = MagicMock()

    result = fig_cards_logic.check_path_blind(path, pointer, board, color, figure_id, figure_type, db)
    
    assert result is False

def test_check_path_blind_invalid_board_figure(fig_cards_logic):
    path = [DirectionEnum.RIGHT, DirectionEnum.RIGHT, DirectionEnum.DOWN]
    pointer = (1, 1)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.GREEN, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.GREEN, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.GREEN, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.GREEN, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )

    color = ColorEnum.RED
    figure_id = 1
    figure_type = "FIGE05"
    board_figure = [
        BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=3, highlighted=False),
        BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=3, highlighted=False),
        BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=3, highlighted=False),
        BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=4, highlighted=False)
    ]
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_path_blind(path, pointer, board, color, figure_id, figure_type, db, board_figure)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Boxes given out of type figure bounds"

def test_get_pointer_from_figure(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01),
        BoxOut(id=2, color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=1, pos_y=3, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01)
    ]

    result = fig_cards_logic.get_pointer_from_figure(figure, 0)
    assert result == (1, 1)

    result = fig_cards_logic.get_pointer_from_figure(figure, 1)
    assert result == (1, 3)

    result = fig_cards_logic.get_pointer_from_figure(figure, 2)
    assert result == (1, 3)

    result = fig_cards_logic.get_pointer_from_figure(figure, 3)
    assert result == (1, 1)
    
def test_get_pointer_from_figure_empty_figure(fig_cards_logic):
    figure = []

    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.get_pointer_from_figure(figure, 0)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Empty figure"
    
def test_get_pointer_from_figure_invalid_rotation(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01)
    ]

    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.get_pointer_from_figure(figure, 4)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Invalid rotation"

def test_check_valid_figure_success(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=2, color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05)
    ]

    fig_cards_logic.get_pointer_from_figure = MagicMock(side_effect=lambda figure, rotation: (figure[0].pos_x, figure[0].pos_y) if rotation == 0 else (figure[1].pos_x, figure[1].pos_y) if rotation == 1 else (figure[2].pos_x, figure[2].pos_y) if rotation == 2 else (figure[3].pos_x, figure[3].pos_y))
    fig_cards_logic.is_valid_pointer = MagicMock(side_effect=lambda pointer: True)
    fig_cards_logic.belongs_to_figure = MagicMock(side_effect=lambda pointer, figure: any(box["pos_x"] == pointer[0] and box["pos_y"] == pointer[1] for box in figure))
    fig_cards_logic.check_path_blind = MagicMock(side_effect=lambda path, pointer, board, color, figure_id, figure_type, db, board_figure: True)

    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )
    figure_type = "FIGE05"
    db = MagicMock()
    
    result = fig_cards_logic.check_valid_figure(figure, figure_type, board, db)
    assert result is True

def test_check_valid_figure_invalid_figure_color(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.GREEN, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=2, color=ColorEnum.GREEN, pos_x=2, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.GREEN, pos_x=3, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.GREEN, pos_x=3, pos_y=2, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05)
    ]

    fig_cards_logic.get_pointer_from_figure = MagicMock(side_effect=lambda figure, rotation: (figure[0].pos_x, figure[0].pos_y) if rotation == 0 else (figure[1].pos_x, figure[1].pos_y) if rotation == 1 else (figure[2].pos_x, figure[2].pos_y) if rotation == 2 else (figure[3].pos_x, figure[3].pos_y))
    fig_cards_logic.belongs_to_figure = MagicMock(side_effect=lambda pointer, figure: any(box["pos_x"] == pointer[0] and box["pos_y"] == pointer[1] for box in figure))
    fig_cards_logic.check_path_blind = MagicMock(side_effect=lambda path, pointer, board, color, figure_id, figure_type, db, board_figure: True)

    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )

    figure_type = "FIGE05"
    db = MagicMock()


    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_valid_figure(figure, figure_type, board, db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Color of figure does not match with color in board"

def test_check_valid_figure_invalid_figure(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=2, color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=4, pos_y=2, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05)
    ]

    fig_cards_logic.get_pointer_from_figure = MagicMock(side_effect=lambda figure, rotation: (figure[0].pos_x, figure[0].pos_y) if rotation == 0 else (figure[1].pos_x, figure[1].pos_y) if rotation == 1 else (figure[2].pos_x, figure[2].pos_y) if rotation == 2 else (figure[3].pos_x, figure[3].pos_y))
    fig_cards_logic.belongs_to_figure = MagicMock(side_effect=lambda pointer, figure: any(box["pos_x"] == pointer[0] and box["pos_y"] == pointer[1] for box in figure))
    fig_cards_logic.check_path_blind = MagicMock(side_effect=lambda path, pointer, board, color, figure_id, figure_type, db, board_figure: {'message': "Boxes given out of type figure bounds"})

    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )

    figure_type = "FIGE05"
    db = MagicMock()


    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_valid_figure(figure, figure_type, board, db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Boxes given out of type figure bounds"

def test_check_valid_figure_invalid_figure_type(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG05),
        BoxOut(id=2, color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False, figure_id=1, figure_type=typeEnum.FIG05)
    ]

    fig_cards_logic.get_pointer_from_figure = MagicMock(side_effect=lambda figure, rotation: (figure[0].pos_x, figure[0].pos_y) if rotation == 0 else (figure[1].pos_x, figure[1].pos_y) if rotation == 1 else (figure[2].pos_x, figure[2].pos_y) if rotation == 2 else (figure[3].pos_x, figure[3].pos_y))
    fig_cards_logic.belongs_to_figure = MagicMock(side_effect=lambda pointer, figure: any(box["pos_x"] == pointer[0] and box["pos_y"] == pointer[1] for box in figure))
    fig_cards_logic.check_path_blind = MagicMock(side_effect=lambda path, pointer, board, color, figure_id, figure_type, db, board_figure: False)

    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=0, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=0, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=1, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=2, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=3, highlighted=False)],
            [BoxOut(color=ColorEnum.BLUE, pos_x=0, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=1, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=2, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=3, pos_y=4, highlighted=False),
            BoxOut(color=ColorEnum.BLUE, pos_x=4, pos_y=4, highlighted=False)]
        ],
        formed_figures=[]
    )

    figure_type = "FIG050"
    db = MagicMock()


    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_valid_figure(figure, figure_type, board, db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Invalid figure type"

@pytest.mark.asyncio
async def test_play_figure_card_success(fig_cards_logic, game_logic):
    game_id = 1
    figure_card = FigureCard(id=1, player_id=1, game_id=1, type="FIGE05", show=True, blocked=False)
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=2, color=ColorEnum.RED, pos_x=2, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=3, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=3, pos_y=2, highlighted=False, figure_id=1, figure_type=typeEnum.FIGE05)
    ]

    figureInfo = PlayFigureCardInput(player_id=1, game_id=1, card_id=1, figure=figure)

    fig_cards_logic.check_game_exists = MagicMock(side_effect=lambda game_id, db: True)
    fig_cards_logic.check_game_exists = MagicMock(side_effect=lambda game_id, db: True)
    fig_cards_logic.game_state_repo.get_game_state_by_id = MagicMock(side_effect=lambda game_id, db: GameStateInDB(id=1, game_id=1, state=StateEnum.PLAYING, current_player=1))
    fig_cards_logic.player_repo.get_player_by_id = MagicMock(side_effect=lambda game_id, player_id, db: Player(id=1, name='Coco', game_id=1, game_state_id=1,turn=True, host=True, winner=False))

    fig_cards_logic.check_valid_figure = MagicMock(side_effect=lambda figure, figure_type, board, db: True)
    fig_cards_logic.get_pointer_from_figure = MagicMock(side_effect=lambda figure, rotation: (figure[0].pos_x, figure[0].pos_y) if rotation == 0 else (figure[1].pos_x, figure[1].pos_y) if rotation == 1 else (figure[2].pos_x, figure[2].pos_y) if rotation == 2 else (figure[3].pos_x, figure[3].pos_y))
    fig_cards_logic.is_valid_pointer = MagicMock(side_effect=lambda pointer: True)
    fig_cards_logic.belongs_to_figure = MagicMock(side_effect=lambda pointer, figure: any(box["pos_x"] == pointer[0] and box["pos_y"] == pointer[1] for box in figure))
    fig_cards_logic.check_path_blind = MagicMock(side_effect=lambda path, pointer, board, color, figure_id, figure_type, db, board_figure: True)
    fig_cards_logic.fig_card_repo.get_figure_card_by_id.return_value = figure_card
    fig_cards_logic.fig_card_repo.update_figure_card.return_value = figure_card
    db = MagicMock()
    

    game_logic.check_win_condition_no_figure_cards = MagicMock(side_effect=lambda game_id, player_id, db: False) # no funciona el mock

    with patch('game.game_logic.get_game_logic', return_value=game_logic): # no funciona el mock
        with patch('connection_manager.ConnectionManager.broadcast', new_callable=AsyncMock) as mock_broadcast:
            result = await fig_cards_logic.play_figure_card(figureInfo, db)
            assert result['message'] == "Figure card played"
            mock_broadcast.assert_has_calls([
                call({'type': 'PLAYER_WINNER', 'game_id': 1, 'winner_id': 1, 'winner_name': 'Coco'}), # como no puedo mockear el game logic, uso el retorno de True
                call({'type': f"{figureInfo.game_id}:FIGURE_UPDATE"})
            ])

def test_is_pointer_different_from_formed_figures(fig_cards_logic):
    pointer = (2, 3)
    
    figures = [
        [
            BoxOut(id=1, color=ColorEnum.RED, pos_x=0, pos_y=0, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01),
            BoxOut(id=2, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01)
        ],
        [
            BoxOut(id=3, color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False, figure_id=2, figure_type=typeEnum.FIG02),
            BoxOut(id=4, color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False, figure_id=2, figure_type=typeEnum.FIG02)
        ]
    ]
    
    result = fig_cards_logic.is_pointer_different_from_formed_figures(pointer, figures)
    assert result is False

    pointer = (4, 4)
    result = fig_cards_logic.is_pointer_different_from_formed_figures(pointer, figures)
    assert result == pointer


def test_check_need_to_unblock_card_one_card_blocked(fig_cards_logic):
    game_id = 1
    player_id = 1
    mock_db = MagicMock(spec=Session)

    fig_cards_logic.fig_card_repo.get_figure_cards.return_value = [
        FigureCard(id=1, player_id=player_id, game_id=game_id, type="FIG01", show=True, blocked=True)
    ]

    unblocked = fig_cards_logic.check_need_to_unblock_card(game_id, player_id, mock_db)

    assert unblocked
    fig_cards_logic.fig_card_repo.unblock_figure_card.assert_called_once_with(1, mock_db)
    fig_cards_logic.fig_card_repo.soft_block_figure_card.assert_called_once_with(1, mock_db)


def test_check_need_to_unblock_card_one_card_not_blocked(fig_cards_logic):
    game_id = 1
    player_id = 1
    mock_db = MagicMock(spec=Session)

    fig_cards_logic.fig_card_repo.get_figure_cards.return_value = [
        FigureCard(id=1, player_id=player_id, game_id=game_id, type="FIG01", show=True, blocked=False)
    ]

    unblocked = fig_cards_logic.check_need_to_unblock_card(game_id, player_id, mock_db)

    assert not unblocked
    fig_cards_logic.fig_card_repo.unblock_figure_card.assert_not_called()
    fig_cards_logic.fig_card_repo.soft_block_figure_card.assert_not_called()

    
    
def test_check_need_to_unblock_multiple_cards_one_blocked(fig_cards_logic):
    game_id = 1
    player_id = 1
    mock_db = MagicMock(spec=Session)

    fig_cards_logic.fig_card_repo.get_figure_cards.return_value = [
        FigureCard(id=1, player_id=player_id, game_id=game_id, type="FIG01", show=True, blocked=True),
        FigureCard(id=2, player_id=player_id, game_id=game_id, type="FIG01", show=True, blocked=False)
    ]

    unblocked = fig_cards_logic.check_need_to_unblock_card(game_id, player_id, mock_db)

    assert not unblocked
    fig_cards_logic.fig_card_repo.unblock_figure_card.assert_not_called()
    fig_cards_logic.fig_card_repo.soft_block_figure_card.assert_not_called()

    
def test_check_need_to_unblock_multiple_cards_none_blocked(fig_cards_logic):
    game_id = 1
    player_id = 1
    mock_db = MagicMock(spec=Session)

    fig_cards_logic.fig_card_repo.get_figure_cards.return_value = [
        FigureCard(id=1, player_id=player_id, game_id=game_id, type="FIG01", show=True, blocked=False),
        FigureCard(id=2, player_id=player_id, game_id=game_id, type="FIG01", show=True, blocked=False)
    ]

    unblocked = fig_cards_logic.check_need_to_unblock_card(game_id, player_id, mock_db)

    assert not unblocked
    fig_cards_logic.fig_card_repo.unblock_figure_card.assert_not_called()
    fig_cards_logic.fig_card_repo.soft_block_figure_card.assert_not_called()


def test_check_need_to_unblock_no_cards(fig_cards_logic):
    game_id = 1
    player_id = 1
    mock_db = MagicMock(spec=Session)

    fig_cards_logic.fig_card_repo.get_figure_cards.return_value = []

    fig_cards_logic.check_need_to_unblock_card(game_id, player_id, mock_db)

    fig_cards_logic.fig_card_repo.unblock_figure_card.assert_not_called()
    fig_cards_logic.fig_card_repo.soft_block_figure_card.assert_not_called()


def test_check_valid_block_card_not_shown(fig_cards_logic, fig_card_repo, mock_db):
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=1, figure_type=typeEnum.FIG01)]
    )
    

    fig_card_repo.get_figure_card_by_id.return_value = MagicMock(show=False)
    
    is_valid = fig_cards_logic.check_valid_block(figureInfo, mock_db)
    assert not is_valid


def test_check_valid_block_card_already_blocked(fig_cards_logic, fig_card_repo, mock_db):
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=1, figure_type=typeEnum.FIG01)]
    )

    fig_card_repo.get_figure_card_by_id.return_value = MagicMock(show=True)
    
    fig_card_repo.get_figure_cards.return_value = [
        MagicMock(blocked=True, show=True), 
        MagicMock(blocked=False, show=True),
    ]

    is_valid = fig_cards_logic.check_valid_block(figureInfo, mock_db)
    assert not is_valid


def test_check_valid_block_only_one_card_shown(fig_cards_logic, fig_card_repo, mock_db):
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=1, figure_type=typeEnum.FIG01)]
    )

    fig_card_repo.get_figure_card_by_id.return_value = MagicMock(show=True)
    
    fig_card_repo.get_figure_cards.return_value = [
        MagicMock(blocked=False, show=True),
    ]

    is_valid = fig_cards_logic.check_valid_block(figureInfo, mock_db)
    assert not is_valid


def test_check_valid_block_wrong_figure(fig_cards_logic, fig_card_repo, mock_db):
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=2, figure_type=typeEnum.FIG01)]
    )

    fig_card_repo.get_figure_card_by_id.return_value = MagicMock(show=True)
    
    fig_card_repo.get_figure_cards.return_value = [
        MagicMock(blocked=False, show=True),
        MagicMock(blocked=False, show=True),
    ]
    
    fig_cards_logic.board_repo.get_configured_board.return_value = MagicMock()
    fig_cards_logic.check_valid_figure = MagicMock()
    fig_cards_logic.check_valid_figure.return_value = False
    mock_game_state = MagicMock(state="PLAYING")
    mock_game = MagicMock(game_state=mock_game_state)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_game
    is_valid = fig_cards_logic.check_valid_block(figureInfo, mock_db)
    assert not is_valid

def test_check_valid_block_forbidden_color(fig_cards_logic, fig_card_repo, mock_db):
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=1, figure_type=typeEnum.FIG01)]
    )

    fig_card_repo.get_figure_card_by_id.return_value = MagicMock(show=True, type=typeEnum.FIG01)
    
    fig_card_repo.get_figure_cards.return_value = [
        MagicMock(blocked=False, show=True),
        MagicMock(blocked=False, show=True),
    ]
    
    fig_cards_logic.board_repo.get_configured_board.return_value = MagicMock()
    fig_cards_logic.check_valid_figure = MagicMock()
    fig_cards_logic.check_valid_figure.return_value = True
    fig_cards_logic.game_state_repo.get_game_state_by_id.return_value = MagicMock(state="PLAYING", forbidden_color=ColorEnum.RED)
    mock_game_state = MagicMock(state="PLAYING")
    mock_game = MagicMock(game_state=mock_game_state)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_game

    is_valid = fig_cards_logic.check_valid_block(figureInfo, mock_db)
    assert not is_valid

def test_check_valid_block_success(fig_cards_logic, fig_card_repo, mock_db):
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=1, figure_type=typeEnum.FIG01)]
    )

    fig_card_repo.get_figure_card_by_id.return_value = MagicMock(show=True, type=typeEnum.FIG01)
    
    fig_card_repo.get_figure_cards.return_value = [
        MagicMock(blocked=False, show=True),
        MagicMock(blocked=False, show=True),
    ]

    fig_cards_logic.board_repo.get_configured_board.return_value = MagicMock()
    fig_cards_logic.check_valid_figure = MagicMock()
    fig_cards_logic.check_valid_figure.return_value = True
    mock_game_state = MagicMock(state="PLAYING")
    mock_game = MagicMock(game_state=mock_game_state)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_game

    is_valid = fig_cards_logic.check_valid_block(figureInfo, mock_db)
    assert is_valid


@pytest.mark.asyncio
async def test_block_figure_card_success(fig_cards_logic, mock_db):
    game_id = 1
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=1, figure_type=typeEnum.FIG01)]
    )
    fig_cards_logic.check_valid_block = MagicMock(return_value=True)
    
    with patch('connection_manager.ConnectionManager.broadcast', new_callable=AsyncMock) as mock_broadcast:
        fig_cards_logic.fig_card_repo.block_figure_card = MagicMock()
        
        await fig_cards_logic.block_figure_card(figureInfo, mock_db)
        
        fig_cards_logic.check_valid_block.assert_called_once_with(
            figureInfo, mock_db
        )
        
        mock_broadcast.assert_any_call({"type": f"{game_id}:BLOCK_CARD"})
        
        mock_broadcast.assert_any_call({"type": f"{game_id}:BOARD_UPDATE"})

        fig_cards_logic.fig_card_repo.block_figure_card.assert_called_once_with(
            figureInfo.game_id, figureInfo.card_id, mock_db
        )
        fig_cards_logic.partial_mov_repo.partial_mov_repo.delete_all_partial_movements_by_player(figureInfo.blocker_player_id, mock_db)
        fig_cards_logic.mov_card_repo.discard_all_player_partially_used_cards(figureInfo.blocker_player_id, mock_db)


@pytest.mark.asyncio
async def test_block_figure_card_invalid_block(fig_cards_logic, mock_db):
    figureInfo = BlockFigureCardInput(
        game_id=1,
        blocker_player_id=2,
        blocked_player_id=1,
        card_id=1,
        figure=[ BoxOut(pos_x = 0,  pos_y = 0, color = ColorEnum.RED, highlighted=True, figure_id=1, figure_type=typeEnum.FIG01)]
    )
    
    fig_cards_logic.check_valid_block = MagicMock(return_value=False)
    
    with patch('connection_manager.ConnectionManager.broadcast', new_callable=AsyncMock) as mock_broadcast:
        fig_cards_logic.fig_card_repo.block_figure_card = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            await fig_cards_logic.block_figure_card(figureInfo, mock_db)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Invalid blocking"
        
        fig_cards_logic.check_valid_block.assert_called_once_with(
            figureInfo, mock_db
        )
        
        mock_broadcast.assert_not_called()
        
        fig_cards_logic.fig_card_repo.block_figure_card.assert_not_called()
