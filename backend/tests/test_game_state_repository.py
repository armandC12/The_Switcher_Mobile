import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException

from board.models import ColorEnum
from gameState.game_state_repository import GameStateRepository
from gameState.models import GameState, StateEnum
from game.models import Game
from game.schemas import GameCreate
from player.schemas import PlayerCreateMatch
from game.game_repository import GameRepository
from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def game_state_repository():
    return GameStateRepository()


@pytest.fixture
def game_repository():
    return GameRepository()
        

@pytest.mark.integration_test
def test_get_game_state_by_id(game_state_repository: GameStateRepository, session):
    test_game_state = session.query(GameState).filter(GameState.game_id == 1).one()
    game_state = game_state_repository.get_game_state_by_id(1, session)

    assert test_game_state.id == game_state.id


@pytest.mark.integration_test
def test_get_game_state_by_id_not_found(game_state_repository: GameStateRepository, session):
    game_id = 999
    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.get_game_state_by_id(game_id, session)
    assert excinfo.value.status_code == 404
    assert "Game State not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_update_game_state(game_state_repository: GameStateRepository, session):
    game_state_repository.update_game_state(1, StateEnum.PLAYING, session)
    game_state = game_state_repository.get_game_state_by_id(1, session)
    
    assert game_state.state == StateEnum.PLAYING


@pytest.mark.integration_test
def test_update_game_state_no_game_state(game_state_repository: GameStateRepository, session):
    game_id = 999
    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.update_game_state(game_id, StateEnum.FINISHED, session)
    assert excinfo.value.status_code == 404
    assert "Game State not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_update_current_player(game_state_repository: GameStateRepository, session):
    game_state_repository.update_current_player(game_id=1, first_player_id=2, db=session)
    
    updated_game_state = session.query(GameState).filter(GameState.game_id == 1).one()
    
    assert updated_game_state.current_player == 2


@pytest.mark.integration_test
def test_update_current_player_no_game_state(game_state_repository: GameStateRepository, session):
    game_id = 999 # id exageradamente grande
    player_id = 1 # cualquier id basta total salta primero la exception game state not found
    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.update_current_player(game_id, player_id, session)
    assert excinfo.value.status_code == 404
    assert "Game State not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_next_player_id(game_state_repository: GameStateRepository, session):
    test_game_state = session.query(GameState).filter(GameState.game_id == 1,
                                                        GameState.id == 1).one()
    
    current_player_id = test_game_state.current_player

    result = game_state_repository.get_next_player_id(1, session)
    
    assert result == 3


@pytest.mark.integration_test
def test_get_next_player_id_no_game_state(game_state_repository: GameStateRepository, session):
    game = Game(name="Test game", min_players=2, max_players=4)
    session.add(game)
    session.commit()

    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.get_next_player_id(game.id, session)

    assert excinfo.value.status_code == 404
    assert "Game State not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_next_player_id_no_players(game_state_repository: GameStateRepository, session):
    game = Game(name="Test game", min_players=2, max_players=4)
    session.add(game)
    session.commit()    

    game_state = GameState(state=StateEnum.WAITING, game_id=game.id)
    session.add(game_state)
    session.commit()
    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.get_next_player_id(game.id, session)

    assert excinfo.value.status_code == 404
    assert "Players not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_next_player_id_no_current_player(game_state_repository: GameStateRepository, 
                                              game_repository: GameRepository, session):
    
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False), 
                                      PlayerCreateMatch(name="Test Player"), session)

    game_id = res['game'].id

    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.get_next_player_id(game_id, session)

    assert excinfo.value.status_code == 404
    assert "Current player not found" in str(excinfo.value.detail)


# @pytest.mark.integration_test
# def test_get_next_player_id_no_next_player(game_state_repository: GameStateRepository, 
#                                        game_repository: GameRepository, session):
    
#     res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2), 
#                                         PlayerCreateMatch(name="Test Player"), session)

#     game_id = res['game'].id
#     player_id = res["player"].id
#     print(player_id)
#     game_state_repository.update_current_player(game_id, player_id, session)
#     next_player = game_state_repository.get_next_player_id(game_id, session)
#     print(next_player)

#     with pytest.raises(HTTPException) as excinfo:
#         next_player = game_state_repository.get_next_player_id(game_id, session)

#     assert excinfo.value.status_code == 404
#     assert "Next player not found" in str(excinfo.value.detail)

@pytest.mark.integration_test
def test_get_current_player_success(game_state_repository: GameStateRepository, 
                            game_repository: GameRepository, session):

    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False), 
                                      PlayerCreateMatch(name="Test Player"), session)
    game_id = res['game'].id
    player_id = res["player"].id

    game_state_repository.update_current_player(game_id, player_id, session)
    
    current_player = game_state_repository.get_current_player(game_id, session)

    assert player_id == current_player['current_player_id']


@pytest.mark.integration_test
def test_get_current_player_no_game_state(game_state_repository: GameStateRepository, 
                            game_repository: GameRepository, session):
    game = Game(name="Test game", min_players=2, max_players=4)
    session.add(game)
    session.commit() 
    
    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.get_current_player(game.id, session)
    assert excinfo.value.status_code == 404
    assert "Game State not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_current_player_no_current_player(game_state_repository: GameStateRepository, 
                            game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False), 
                                      PlayerCreateMatch(name="Test Player"), session)
    
    with pytest.raises(HTTPException) as excinfo:
        game_state_repository.get_current_player(res['game'].id, session)
    assert excinfo.value.status_code == 404
    assert "Current player not found" in str(excinfo.value.detail)

@pytest.mark.integration_test
def test_update_forbidden_color(game_state_repository: GameStateRepository, session):

    game_state_repository.update_forbidden_color(1, "RED", session)
    game_state = game_state_repository.get_game_state_by_id(1, session)
    
    assert game_state.forbidden_color == ColorEnum.RED