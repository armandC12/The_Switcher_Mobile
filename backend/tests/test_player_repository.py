import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException

from game.game_repository import GameRepository
from game.schemas import GameCreate
from game.models import Game
from game.game_logic import get_game_logic

from gameState.models import StateEnum, GameState
from gameState.game_state_repository import GameStateRepository

from player.player_repository import PlayerRepository
from player.models import Player, turnEnum
from player.schemas import PlayerCreateMatch

from movementCards.models import MovementCard, typeEnum
from movementCards.movement_cards_repository import MovementCardsRepository

from figureCards.figure_cards_repository import FigureCardsRepository

from partial_movement.models import PartialMovements

from database.db import engine

import pdb
#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def player_repo():
    return PlayerRepository()

@pytest.fixture
def game_repo():
    return GameRepository()

@pytest.fixture
def game_state_repo():
    return GameStateRepository()

@pytest.fixture
def mov_card_repo():
    return MovementCardsRepository()

@pytest.fixture
def fig_card_repo():
    return FigureCardsRepository()

@pytest.fixture
def game_logic(game_repo, game_state_repo, player_repo, fig_card_repo):
    return get_game_logic(game_repo, game_state_repo, player_repo, fig_card_repo)

@pytest.fixture
def setup_game_player(session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.flush()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.flush()

    players = [
        Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=False, turn=turnEnum.SEGUNDO ,winner=False),
        Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=True, turn=turnEnum.PRIMERO , winner=False),
        Player(name="Player3", game_id=game.id, game_state_id=game_state.id, host=False, turn=turnEnum.TERCERO , winner=False)

        ]
    session.add_all(players)
    session.flush()

    # Crear cartas de movimiento
    movement_cards = [
        MovementCard(type="LINEAL_CONT", description="Test Card 1", player_id=players[0].id, used = True, game_id=game.id),
        MovementCard(type="DIAGONAL_CONT", description="Test Card 2", player_id=players[0].id, used = True, game_id=game.id),
        MovementCard(type="EN_L_DER", description="Test Card 3", player_id=players[0].id, used = False , game_id=game.id),
        MovementCard(type="LINEAL_CONT", description="Test Card 4", player_id=players[1].id , used = True , game_id=game.id),
        MovementCard(type="DIAGONAL_CONT", description="Test Card 5", player_id=players[1].id, used = False , game_id=game.id),
        MovementCard(type="EN_L_DER", description="Test Card 6", player_id=players[1].id, used = False, game_id=game.id),
        MovementCard(type="LINEAL_CONT", description="Test Card 7", used = False, game_id=game.id),
        MovementCard(type="DIAGONAL_CONT", description="Test Card 8", used = False, game_id=game.id),
        MovementCard(type="EN_L_DER", description="Test Card 9", used = False, game_id=game.id),
    ]
    session.add_all(movement_cards)
    session.commit()

    
    return game, game_state, players, movement_cards

@pytest.mark.integration_test
def test_get_player_by_id(player_repo: PlayerRepository, session):
    # session = Session()
    try:
        test_player = session.query(Player).filter(Player.game_id == 1,
                                                   Player.id == 1).one()

        player_in_db = player_repo.get_player_by_id(1, 1, session)

        assert player_in_db.id == test_player.id
    except NoResultFound:
        raise ValueError("There is no player with id=1 in game with id=1")
    

@pytest.mark.integration_test
def test_get_player_by_id_no_player(player_repo: PlayerRepository, session):
    
    with pytest.raises(HTTPException) as exc_info:
        player_repo.get_player_by_id(121, 121, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There is no such player"
    

@pytest.mark.integration_test
def test_get_players_in_game(player_repo: PlayerRepository, session):
    N_players = session.query(Player).filter(Player.game_id == 1).count()

    players_in_game = player_repo.get_players_in_game(1, session)

    assert len(players_in_game) == N_players

    
@pytest.mark.integration_test
def test_get_players_in_game_no_players(player_repo: PlayerRepository, session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.flush()
    
    game_state = GameState(game_id = game.id, state=StateEnum.FINISHED)
    session.add(game_state)
    
    players_in_game = player_repo.get_players_in_game(game.id, session)

    assert len(players_in_game) == 0


@pytest.mark.integration_test
def test_get_players_in_game_no_game(player_repo: PlayerRepository, session):
    game_id = 676
    with pytest.raises(HTTPException) as exc_info:
        players_in_game = player_repo.get_players_in_game(game_id, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Game {game_id} not found"


@pytest.mark.integration_test     
def test_assign_turn_player(game_repo: GameRepository, player_repo: PlayerRepository, session):    
    res = game_repo.create_game(GameCreate(name="Test Player Game", max_players=4, min_players=2, password=None, is_private=False), 
                                      PlayerCreateMatch(name="Test Player"), 
                                      session)
    
    game = res.get('game')
    player = res.get('player')

    player_repo.assign_turn_player(game.id, player.id, turnEnum.SEGUNDO, session)
        
    updated_player = session.query(Player).filter(Player.id == player.id).one()
        
    assert updated_player.turn == turnEnum.SEGUNDO
    

@pytest.mark.integration_test     
def test_assign_turn_player_no_player(game_repo: GameRepository, player_repo: PlayerRepository, session):    
    res = game_repo.create_game(GameCreate(name="Test Player Game", max_players=4, min_players=2, password=None, is_private=False), 
                                      PlayerCreateMatch(name="Test Player"), 
                                      session)
    
    game = res.get('game')
    with pytest.raises(HTTPException) as exc_info:
        player_repo.assign_turn_player(game.id, 800, turnEnum.SEGUNDO, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There is no such player"
        
        


@pytest.mark.integration_test
def test_create_player_success(player_repo: PlayerRepository,game_repo: GameRepository, session):
    res = game_repo.create_game(GameCreate(name="Test Game", max_players=4, min_players=2, password=None, is_private=False), 
                                      PlayerCreateMatch(name="Test Player"), 
                                      session)
    
    game = res.get('game')

    player_data = player_repo.create_player(game_id=game.id, player_name="Test Player", db=session)

    new_player = session.query(Player).filter(Player.id == player_data["player_id"]).first()

    assert new_player is not None
    assert new_player.name == "Test Player"
    assert new_player.host is False
    assert new_player.winner is False


@pytest.mark.integration_test
def test_create_player_fail(player_repo: PlayerRepository,game_repo: GameRepository, session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.flush()

    with pytest.raises(HTTPException) as exc_info:
        player_repo.create_player(game_id=game.id, player_name="Test Player", db=session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No game status for game"


@pytest.mark.asyncio
@pytest.mark.integration_test
async def test_leave_game_player_turn(session, player_repo, game_repo, game_state_repo, mov_card_repo, game_logic, setup_game_player):
    game, game_state, players, mov_cards = setup_game_player
    player1_id = players[0].id
    player2_id = players[1].id
    player3_id = players[2].id
    
    #Creo mov parciales para el jugador
    partial_movs = [PartialMovements(
                        pos_from_x = 0,
                        pos_from_y = 0,
                        pos_to_x = 1,
                        pos_to_y = 1, 
                        game_id = 1,
                        player_id = player1_id,
                        mov_card_id = mov_cards[0].id
                    ), 
                    PartialMovements(
                        pos_from_x = 4,
                        pos_from_y = 3,
                        pos_to_x = 1,
                        pos_to_y = 0, 
                        game_id = 1,
                        player_id = player1_id,
                        mov_card_id = mov_cards[1].id
                    )
                ]

    session.add_all(partial_movs)
    session.commit()
    
    # El jugador de turno es quien quiere salir
    game_state_repo.update_current_player(game.id, players[0].id, session)

    #pdb.set_trace()

    # Llamamos a leave game
    result = await player_repo.leave_game(game_id=game.id, player_id=players[0].id, game_logic=game_logic, game_repo=game_repo, game_state_repo=game_state_repo, mov_card_repo=mov_card_repo, db=session)

    # Verificamos el jugador ha abandonado la partida exitosamente
    assert result == {"message": "Player has successfully left the game", "changed_turn": True}
    
    #pdb.set_trace()
    ## Verificamos se eliminó al jugador
    players_in_game = session.query(Player).filter(Player.game_id == game.id).all()
    assert len(players_in_game) == 2

    # Verificamos hay 6 cartas de mov en el mazo
    discarded_cards = session.query(MovementCard).filter(MovementCard.player_id == None).all()
    assert len(discarded_cards) == 6
    
    #Verificamos solo 3 de ellas son marcadas como usadas
    discarded_cards = session.query(MovementCard).filter(MovementCard.player_id == None, MovementCard.used == True).all()
    assert len(discarded_cards) == 3
    

    # Verifico los movimientos parciales han sido eliminados
    deleted_partial_movements = session.query(PartialMovements).filter(PartialMovements.game_id == game.id).all()
    assert len(deleted_partial_movements) == 0

    # Verifico el turno le pertenece al otro jugador
    updated_game_state = game_state_repo.get_game_state_by_id(game.id, session)
    assert updated_game_state.current_player == player3_id


@pytest.mark.integration_test
def test_assign_winner_of_game(player_repo: PlayerRepository, session, setup_game_player):
    game, game_state, players, movement_cards = setup_game_player
    
    # Asignar ganador
    player_repo.assign_winner_of_game(game_id=game.id, player_id=players[0].id, db=session)
    
    # Verificar que el jugador haya sido marcado como ganador
    updated_player = session.query(Player).filter(Player.id == players[0].id).one()
    assert updated_player.winner is True


@pytest.mark.integration_test
def test_assign_winner_of_no_player(player_repo: PlayerRepository, session):
    with pytest.raises(HTTPException) as exc_info:
        player_repo.assign_winner_of_game(game_id=999, player_id=999, db=session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There is no such player"


@pytest.mark.asyncio
@pytest.mark.integration_test
async def test_player_leave_no_players(player_repo: PlayerRepository, game_logic, game_repo, game_state_repo, mov_card_repo, setup_game_player, session):
    game, game_state, players, mov_cards = setup_game_player
    player1_id = players[0].id
    player2_id = players[1].id
    player3_id = players[2].id
    
    game_state_repo.update_game_state(game_id=game.id, state=StateEnum.FINISHED, db=session)

    with pytest.raises(HTTPException) as exc_info:
        await player_repo.leave_game(game_id=game.id, player_id=999, game_logic=game_logic, game_repo=game_repo, 
                                              game_state_repo=game_state_repo, mov_card_repo=mov_card_repo, db=session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There is no such player"


@pytest.mark.asyncio
@pytest.mark.integration_test
async def test_player_leave_host(player_repo: PlayerRepository, game_logic, game_repo, game_state_repo, mov_card_repo, setup_game_player, session):
    game, game_state, players, mov_cards = setup_game_player
    player1_id = players[0].id
    player2_id = players[1].id
    player3_id = players[2].id
    
    game_state_repo.update_game_state(game_id=game.id, state=StateEnum.WAITING, db=session)

    result = await player_repo.leave_game(game_id=game.id, player_id=player2_id, game_logic=game_logic, game_repo=game_repo, 
                                 game_state_repo=game_state_repo, mov_card_repo=mov_card_repo, db=session)
    
    # me fijo que se haya borrado el juego
    game_in_db = session.query(Game).filter(Game.id == game.id).first()
    players_in_db = session.query(Player).filter(Player.game_id == game.id).first()
    game_state_in_db = session.query(GameState).filter(GameState.game_id == game.id).first()

    assert game_in_db == None
    assert players_in_db == None
    assert game_state_in_db == None

    # Verificamos el jugador ha abandonado la partida exitosamente
    assert result == {"message": "Player has successfully left the game", "changed_turn": False}