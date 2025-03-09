import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import sessionmaker

from board.board_repository import BoardRepository
from board.models import Board, Box, ColorEnum
from board.schemas import BoardOut, BoardAndBoxesOut, BoxOut, BoardPosition
from board.board_logic import BoardLogic, get_board_logic

from database.db import engine

from game.game_repository import GameRepository
from game.schemas import GameCreate
from gameState.game_state_repository import GameStateRepository
from player.schemas import PlayerCreateMatch

from figureCards.models import typeEnum
import pdb; 

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture
def board_repository():
    return BoardRepository()

@pytest.fixture
def board_logic(board_repository):
    return get_board_logic(board_repository)

@pytest.fixture
def game_repository():
    return GameRepository()

@pytest.fixture
def game_state_repository():
    return GameStateRepository()

@pytest.fixture(autouse=True)
def close_session(session):
    yield
    session.close()


@pytest.mark.integration_test
def test_create_new_board(board_repository: BoardRepository, session):
    N_boards = session.query(Board).filter(Board.game_id == 1).count()
    
    board_repository.create_new_board(1, session)
    
    assert session.query(Board).filter(Board.game_id == 1).count() == N_boards + 1


@pytest.mark.integration_test
def test_get_board(board_repository: BoardRepository, session):
    board = board_repository.get_existing_board(1, session)

    assert isinstance(board, BoardOut)
    assert board.game_id == 1
    

@pytest.mark.integration_test
def test_create_new_board_for_existing_private_game(game_repository: GameRepository, board_repository: BoardRepository, session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password="password", is_private=True),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    # le creo un tablero al juego
    board = board_repository.create_new_board(new_game.id, session)
    
    assert isinstance(board, BoardOut)
    assert board.game_id == new_game.id


@pytest.mark.integration_test
def test_create_new_board_for_existing_public_game(game_repository: GameRepository, board_repository: BoardRepository, session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    # le creo un tablero al juego
    board = board_repository.create_new_board(new_game.id, session)
    
    assert isinstance(board, BoardOut)
    assert board.game_id == new_game.id


@pytest.mark.integration_test
def test_create_new_board_for_non_existing_game(board_repository: BoardRepository, session):
    with pytest.raises(HTTPException) as exc_info:
        board_repository.create_new_board(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"


@pytest.mark.integration_test
def test_get_configured_board_for_non_existing_game(board_repository: BoardRepository, session):
    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"


@pytest.mark.integration_test
def test_get_configured_board_for_game_not_started(board_repository: BoardRepository, game_repository: GameRepository, session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Game not started"


@pytest.mark.integration_test
def test_get_configured_board_for_game_with_no_board(   board_repository: BoardRepository, 
                                                        game_repository: GameRepository,
                                                        game_state_repository: GameStateRepository, 
                                                        session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    # inicializo el juego
    game_state_repository.update_game_state(new_game.id, "PLAYING", session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Board not found"

@pytest.mark.integration_test
def test_get_configured_board_for_game_board_with_no_boxes(   board_repository: BoardRepository, 
                                                        game_repository: GameRepository,
                                                        game_state_repository: GameStateRepository, 
                                                        session):

    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    game_state_repository.update_game_state(new_game.id, "PLAYING", session)
    
    board_repository.create_new_board(new_game.id, session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Boxes not found in row 0"

@pytest.mark.integration_test
def test_get_configured_board_for_board_not_configured(board_repository: BoardRepository, game_repository: GameRepository, game_state_repository: GameStateRepository, session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    # inicializo el juego
    game_state_repository.update_game_state(new_game.id, "PLAYING", session)

    # creo un tablero
    board_repository.create_new_board(new_game.id, session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 404
    # assert it contains the string "Boxes not found in row "
    assert "Boxes not found in row " in exc_info.value.detail


@pytest.mark.integration_test
def test_get_configured_board(board_repository: BoardRepository, game_repository: GameRepository, game_state_repository: GameStateRepository, board_logic: BoardLogic, session):
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')
    board_logic.configure_board(new_game.id, session)

    # inicializo el juego
    game_state_repository.update_game_state(new_game.id, "PLAYING", session)
    
    # obtengo el tablero existente (asumiendo que ya esta creado)
    board = board_repository.get_existing_board(new_game.id, session)

    # obtengo el tablero y toda la info de sus boxes (asumiendo que ya esta configurado)
    configured_board = board_repository.get_configured_board(new_game.id, session)
    
    assert isinstance(configured_board, BoardAndBoxesOut)
    assert configured_board.game_id is not None
    assert configured_board.board_id is not None
    #pdb.set_trace()
    assert len(configured_board.boxes) == 6
    for row in configured_board.boxes:
        assert len(row) == 6
        for box in row:
            assert isinstance(box, BoxOut)
            assert box.color.name in [color.name for color in [ColorEnum.BLUE, ColorEnum.GREEN, ColorEnum.RED, ColorEnum.YELLOW]]
            assert box.pos_x in range(6)
            assert box.pos_y in range(6)
    assert configured_board.game_id == new_game.id
    assert configured_board.board_id == board.id


@pytest.mark.integration_test
def test_get_not_configured_board(  board_repository: BoardRepository, 
                                    game_repository: GameRepository, 
                                    game_state_repository: GameStateRepository, 
                                    session):

    # crear partida sin tablero configurado
    new_game = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session).get('game')

    # inicializarla en estado PLAYING
    game_state_repository.update_game_state(new_game.id, "PLAYING", session)
    
    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Board not found"


@pytest.mark.integration_test
def test_add_box_to_existing_board(board_repository: BoardRepository, session):
    # busco un tablero que exista
    existing_board = session.query(Board).first()

    initial_box_count = session.query(Box).filter(Box.board_id == existing_board.id).count()
    
    board_repository.add_box_to_board(existing_board.id, existing_board.game_id, ColorEnum.BLUE, 5, 5, session)
    
    new_box_count = session.query(Box).filter(Box.board_id == existing_board.id).count()
    assert new_box_count == initial_box_count + 1


@pytest.mark.integration_test
def test_switch_boxes(game_repository: GameRepository, board_repository: BoardRepository, session):
    # Crear una partida y un tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    # Creo dos casillas
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.BLUE, pos_from.pos[0], pos_from.pos[1], session)
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.RED, pos_to.pos[0], pos_to.pos[1], session)

    # Verifico colores iniciales
    box_from = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_from.pos[0], Box.pos_y == pos_from.pos[1]).one()
    box_to = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_to.pos[0], Box.pos_y == pos_to.pos[1]).one()
    assert box_from.color == ColorEnum.BLUE
    assert box_to.color == ColorEnum.RED

    # Hacemos el intercambio
    board_repository.switch_boxes(game.id, pos_from, pos_to, session)

    # Verificamos el intercambio
    box_from = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_from.pos[0], Box.pos_y == pos_from.pos[1]).one()
    box_to = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_to.pos[0], Box.pos_y == pos_to.pos[1]).one()
    assert box_from.color == ColorEnum.RED
    assert box_to.color == ColorEnum.BLUE

@pytest.mark.integration_test
def test_switch_boxes_inexistent_box_from(board_repository: BoardRepository, game_repository: GameRepository, session):
    # Crear una partida y un tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    # Creo una casillaa
    pos_from = BoardPosition(pos=(3, 4))
    pos_to = BoardPosition(pos=(1, 1))
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.RED, pos_to.pos[0], pos_to.pos[1], session)

    # Hacemos el intercambio
    with pytest.raises(HTTPException) as exc_info:
        board_repository.switch_boxes(game.id, pos_from, pos_to, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Box not found"


@pytest.mark.integration_test
def test_switch_boxes_inexistent_box_to(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    pos_from = BoardPosition(pos=(0, 0))
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.BLUE, pos_from.pos[0], pos_from.pos[1], session)

    pos_to = BoardPosition(pos=(1, 1))

    with pytest.raises(HTTPException) as exc_info:
        board_repository.switch_boxes(game.id, pos_from, pos_to, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Box not found"
    
@pytest.mark.integration_test
def test_switch_boxes_inexistent_game(board_repository: BoardRepository, session):
    # id de juego que no existe
    game_id = 13434242
    

    # Creo una casilla
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Hacemos el intercambio

    with pytest.raises(HTTPException) as exc_info:
        board_repository.switch_boxes(game_id, pos_from, pos_to, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Game not found"
    
@pytest.mark.integration_test
def test_get_box_by_position(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    pos_from = BoardPosition(pos=(0, 0))
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.BLUE, pos_from.pos[0], pos_from.pos[1], session)

    result = board_repository.get_box_by_position(board.id, 0, 0, session)
    assert result.pos_x == 0
    assert result.pos_y == 0
    assert result.color == 'BLUE'
    
@pytest.mark.integration_test
def test_get_box_by_position_no_box(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_box_by_position(board.id, 10, 10, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Box not found 10, 10"

@pytest.mark.integration_test
def test_highlight_box(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board = board_repository.create_new_board(game.id, session)

    pos_x, pos_y = 0, 0
    initial_color = ColorEnum.RED
    box = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x, pos_y, session)

    board_repository.highlight_box(box.id, session)
    highlighted_box = session.query(Box).filter(Box.id == box.id).first()
    assert highlighted_box.highlight == True
    
@pytest.mark.integration_test
def test_highlight_box_no_box(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board_repository.create_new_board(game.id, session)
    
    with pytest.raises(HTTPException) as exc_info:
        board_repository.highlight_box(999, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Box to highlight not found"

@pytest.mark.integration_test
def test_reset_highlight_for_all_boxes(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board = board_repository.create_new_board(game.id, session)

    pos_x, pos_y = 0, 0
    initial_color = ColorEnum.RED
    box1 = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x, pos_y, session)
    box2 = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x + 1, pos_y, session)
    board_repository.highlight_box(box1.id, session)
    board_repository.highlight_box(box2.id, session)

    highlighted_box1 = session.query(Box).filter(Box.id == box1.id).first()
    highlighted_box2 = session.query(Box).filter(Box.id == box2.id).first()
    assert highlighted_box1.highlight == True
    assert highlighted_box2.highlight == True

    board_repository.reset_highlight_for_all_boxes(game.id, session)
    reset_box1 = session.query(Box).filter(Box.id == box1.id).first()
    reset_box2 = session.query(Box).filter(Box.id == box2.id).first()
    assert reset_box1.highlight == False
    assert reset_box2.highlight == False
    

@pytest.mark.integration_test
def test_reset_highlight_for_all_boxes_no_boxes(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board_repository.create_new_board(game.id, session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.reset_highlight_for_all_boxes(game.id, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No boxes found for the game"
    

@pytest.mark.integration_test
def test_update_figure_id_box(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board = board_repository.create_new_board(game.id, session)

    pos_x, pos_y = 0, 0
    initial_color = ColorEnum.RED
    box = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x, pos_y, session)

    figure_id = 1
    figure_type = typeEnum.FIG01
    board_repository.update_figure_id_box(box.id, figure_id, figure_type, session)
    updated_box = session.query(Box).filter(Box.id == box.id).first()
    assert updated_box.figure_id == figure_id
    assert updated_box.figure_type == figure_type
    
@pytest.mark.integration_test
def test_update_figure_id_box_no_box(board_repository: BoardRepository, game_repository: GameRepository, session):
    # Setup: Create a game and a board
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    
    board_repository.create_new_board(game.id, session)
    
    figure_id = 1
    figure_type = typeEnum.FIG01

    with pytest.raises(HTTPException) as exc_info:
        board_repository.update_figure_id_box(999, figure_id, figure_type, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Box to highlight not found"

@pytest.mark.integration_test
def test_reset_figure_for_all_boxes(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board = board_repository.create_new_board(game.id, session)

    pos_x, pos_y = 0, 0
    initial_color = ColorEnum.RED
    
    box1 = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x, pos_y, session)
    box2 = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x + 1, pos_y, session)
    
    board_repository.update_figure_id_box(box1.id, 1, typeEnum.FIG01, session)
    board_repository.update_figure_id_box(box2.id, 2, typeEnum.FIG02, session)

    updated_box1 = session.query(Box).filter(Box.id == box1.id).first()
    updated_box2 = session.query(Box).filter(Box.id == box2.id).first()
    
    assert updated_box1.figure_id == 1
    assert updated_box1.figure_type == typeEnum.FIG01
    assert updated_box2.figure_id == 2
    assert updated_box2.figure_type == typeEnum.FIG02

    board_repository.reset_figure_for_all_boxes(game.id, session)
    reset_box1 = session.query(Box).filter(Box.id == box1.id).first()
    reset_box2 = session.query(Box).filter(Box.id == box2.id).first()
    
    assert reset_box1.figure_id is None
    assert reset_box1.figure_type is None
    assert reset_box2.figure_id is None
    assert reset_box2.figure_type is None
    
@pytest.mark.integration_test
def test_reset_figure_for_all_boxes_no_boxes(board_repository: BoardRepository, game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board_repository.create_new_board(game.id, session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.reset_figure_for_all_boxes(game.id, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No boxes found for the game"
    

@pytest.mark.integration_test
def test_get_figures(board_repository: BoardRepository, game_repository: GameRepository, session: Session):

    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board = board_repository.create_new_board(game.id, session)

    pos_x, pos_y = 0, 0
    initial_color = ColorEnum.RED
    box1 = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x, pos_y, session)
    box2 = board_repository.add_box_to_board(board.id, game.id, initial_color, pos_x + 1, pos_y, session)
    board_repository.update_figure_id_box(box1.id, 1, typeEnum.FIG01, session)
    board_repository.update_figure_id_box(box2.id, 1, typeEnum.FIG01, session)

    figures = board_repository.get_figures(game.id, session)
    assert len(figures) == 1
    assert len(figures[0]) == 2
    assert figures[0][0]['figure_id'] == 1
    assert figures[0][0]['figure_type'] == typeEnum.FIG01
    assert figures[0][1]['figure_id'] == 1
    assert figures[0][1]['figure_type'] == typeEnum.FIG01


@pytest.mark.integration_test
def test_get_figures_no_boxes(board_repository: BoardRepository, game_repository: GameRepository, session: Session):

    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False),
                                      PlayerCreateMatch(name="Test Player"),
                                      session)
    game = res.get('game')
    board_repository.create_new_board(game.id, session)

    figures = board_repository.get_figures(game.id, session)
    assert figures == []