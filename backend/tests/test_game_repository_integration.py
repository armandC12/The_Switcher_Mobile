import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from game.game_repository import GameRepository
from figureCards.models import FigureCard
from board.models import  Board, Box
from figureCards.models import FigureCard, typeEnum
from game.models import Game
from game.schemas import GameCreate, GameInDB
from game.game_logic import GameLogic
from gameState.models import GameState, StateEnum
from gameState.game_state_repository import GameStateRepository
from movementCards.models import MovementCard
from player.models import Player
from player.schemas import PlayerCreateMatch
from player.player_repository import PlayerRepository
from fastapi import HTTPException

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def game_repository():
    return GameRepository()

@pytest.fixture
def game_state_repository():
    return GameStateRepository()


@pytest.fixture
def player_repository():
    return PlayerRepository()

@pytest.mark.integration_test
def test_get_games(game_repository: GameRepository, session):
    N_games = session.query(Game).join(GameState).filter(GameState.state == StateEnum.WAITING).count()

    list_of_games = game_repository.get_games(session).get('games')

    assert len(list_of_games) == min(5, N_games)


@pytest.mark.integration_test
def test_get_game_by_id(game_repository: GameRepository, session):
    game_id = 1
    game_in_db = session.query(Game).join(GameState).filter(Game.id == game_id).one()

    game = game_repository.get_game_by_id(game_id, session)

    assert game_in_db.id == game.id


@pytest.mark.integration_test
def test_get_game_by_id_not_found(game_repository: GameRepository, session):
    non_existent_game_id = 999
    with pytest.raises(HTTPException) as excinfo:
        game_repository.get_game_by_id(non_existent_game_id, session)
    assert excinfo.value.status_code == 404
    assert "Game not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_count_players_in_game_no_game(game_repository: GameRepository, session):
    non_existent_game_id = 999
    with pytest.raises(HTTPException) as excinfo:
        game_repository.count_players_in_game(non_existent_game_id, session)
    assert excinfo.value.status_code == 404
    assert "Game not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_count_players_in_game(game_repository: GameRepository, session):
    game_id = 1 
    player_count = game_repository.count_players_in_game(game_id, session)

    N_players = session.query(Player).filter(Player.game_id == game_id).count()
    assert player_count == N_players


@pytest.mark.integration_test
def test_get_games_paging(game_repository: GameRepository, session):
    # creo 5 partidas mas la que ya existe para tener mas de 5
    game2 = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False), 
                                        PlayerCreateMatch(name="Test Player"), session)
    game3 = game_repository.create_game(GameCreate(name="Test Game 3", max_players=4, min_players=2, password=None, is_private=False),
                                        PlayerCreateMatch(name="Test Player"), session)
    game4 = game_repository.create_game(GameCreate(name="Test Game 4", max_players=4, min_players=2, password=None, is_private=False), 
                                        PlayerCreateMatch(name="Test Player"), session)
    game5 = game_repository.create_game(GameCreate(name="Test Game 5", max_players=4, min_players=2, password=None, is_private=False), 
                                        PlayerCreateMatch(name="Test Player"), session)
    game6 = game_repository.create_game(GameCreate(name="Test Game 6", max_players=4, min_players=2, password=None, is_private=False), 
                                        PlayerCreateMatch(name="Test Player"), session)
    
    games_page_1 = game_repository.get_games(session, limit=5, offset=0).get('games')
    games_page_2 = game_repository.get_games(session, limit=5, offset=5).get('games')

    assert len(games_page_1) <= 5
    assert len(games_page_2) <= 5
    assert games_page_1 != games_page_2  # Me fijo que haya distintos juegos en cada pagina


@pytest.mark.integration_test
def test_get_game_winner_game_not_found(game_repository: GameRepository, session):
    non_existent_game_id = 999
    with pytest.raises(HTTPException) as excinfo:
        game_repository.get_game_winner(non_existent_game_id, session)
    assert excinfo.value.status_code == 404
    assert "Game not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_game_winner_not_finished(game_repository: GameRepository, session):
    unfinished_game_id = 1
    with pytest.raises(HTTPException) as excinfo:
        game_repository.get_game_winner(unfinished_game_id, session)
    assert excinfo.value.status_code == 404
    assert "The game is not finished" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_game_winner_no_winner(game_repository: GameRepository, game_state_repository: GameStateRepository, session):
    finished_game_id = 1
    game_state_repository.update_game_state(finished_game_id, StateEnum.FINISHED, session)

    not_winner = session.query(Player).filter(Player.game_id == finished_game_id).first()
    assert not_winner != None

    with pytest.raises(HTTPException) as excinfo:
        game_repository.get_game_winner(finished_game_id, session)
    assert excinfo.value.status_code == 404
    assert "There is no winner" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_game_winner(game_repository: GameRepository, player_repository: PlayerRepository, game_state_repository: GameStateRepository, session):
    finished_game_id = 1
    winner = session.query(Player).filter(Player.game_id == finished_game_id).first()
    assert winner != None 
    game_state_repository.update_game_state(finished_game_id, StateEnum.FINISHED, session)

    player_repository.assign_winner_of_game(finished_game_id, winner.id, session)
    
    player = game_repository.get_game_winner(finished_game_id, session)

    assert winner.id == player.id


@pytest.mark.integration_test
def test_get_game_by_id(game_repository: GameRepository, session):
    try:
        test_game = session.query(Game).filter(Game.id == 1).one()

        game = game_repository.get_game_by_id(1, session)

        assert game.get('id') == test_game.id
    except NoResultFound:
        raise ValueError("There is no game with id 1")


@pytest.mark.integration_test
def test_create_game(game_repository: GameRepository, session):
    N_games = session.query(Game).count()

    game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2, password=None, is_private=False),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    
    assert session.query(Game).count() == N_games + 1



@pytest.mark.integration_test
def test_delete_inexistent_game(game_repository: GameRepository, session):    
    inexistent_game_id = 999

    # elimino el juego con id 999
    with pytest.raises(HTTPException) as excinfo:
        game_repository.delete_game(inexistent_game_id, session)

    assert excinfo.value.status_code == 404
    assert f"Game {inexistent_game_id} not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_delete_inexistent_game_state(game_repository: GameRepository, session):    
    game = Game(name="Test game", min_players=2, max_players=4)
    session.add(game)
    session.commit()
    game_id = game.id

    # elimino el juego con id 999
    with pytest.raises(HTTPException) as excinfo:
        game_repository.delete_game(game_id, session)

    assert excinfo.value.status_code == 404
    assert f"GameState not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_delete_game(game_repository: GameRepository, game_state_repository: GameStateRepository, session):    
    game_id = 1
    game_state_repository.update_game_state(game_id, StateEnum.FINISHED, session)

    # elimino el juego con id 1
    game_repository.delete_game(game_id, session)

    game = session.query(Game).filter(Game.id == game_id).first()
    players = session.query(Player).filter(Player.game_id == game_id).first()
    figure_cards = session.query(FigureCard).filter(FigureCard.game_id == game_id).first()
    movement_cards = session.query(MovementCard).filter(MovementCard.game_id == game_id).first()
    game_state = session.query(GameState).filter(GameState.game_id == game_id).first()
    board = session.query(Board).filter(Board.game_id == game_id).first()
    boxes = session.query(Box).filter(Box.game_id == game_id).first()

    assert game == None
    assert players == None
    assert figure_cards == None
    assert movement_cards == None
    assert game_state == None
    assert board == None
    assert boxes == None


@pytest.mark.integration_test
def test_get_games_no_games(game_repository: GameRepository, 
                            game_state_repository: GameStateRepository, session):
    res = game_repository.get_games(session)
    list_of_games = res['games']
    print(list_of_games)
    print(res["total_pages"])
    # borro los juegos existentes
    session.query(Game).delete()
    session.commit()
    
    res = game_repository.get_games(session)
    print(res)
    list_of_games = res['games']
    total_pages = res['total_pages']
    
    assert len(list_of_games) == 0
    assert total_pages == 1