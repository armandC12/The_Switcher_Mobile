import pytest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from board.board_repository import BoardRepository
from board.schemas import BoardPosition
from database.db import engine

from game.models import Game
from gameState.models import GameState, StateEnum
from player.models import Player
from movementCards.models import MovementCard, typeEnum
from partial_movement.models import PartialMovements

from partial_movement.partial_movement_repository import PartialMovementRepository


#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def partial_movement_repo():
    return PartialMovementRepository()

@pytest.fixture
def setup_game_player_card(session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.commit()

    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()

    card = MovementCard(player_id = player.id ,game_id=game.id,type=typeEnum.DIAGONAL_CONT, description = '', used= False)
    session.add(card)
    session.commit()
    
    return game, player, card

@pytest.mark.integration_test
def test_create_partial_movement(partial_movement_repo, session, setup_game_player_card):
    game, player, card = setup_game_player_card
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Call the method to create a partial movement
    partial_movement_repo.create_partial_movement(game.id, player.id, card.id, pos_from, pos_to, session)

    # Verify that the partial movement was created
    partial_movement = session.query(PartialMovements).filter_by(game_id=game.id, player_id=player.id, mov_card_id=card.id).one()
    assert partial_movement.pos_from_x == pos_from.pos[0]
    assert partial_movement.pos_from_y == pos_from.pos[1]
    assert partial_movement.pos_to_x == pos_to.pos[0]
    assert partial_movement.pos_to_y == pos_to.pos[1]

@pytest.mark.integration_test
def test_create_partial_movement_no_game(partial_movement_repo, session):
    non_existent_game_id = 9999
    non_existent_player_id = 9999
    non_existent_card_id = 9999
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar el juego deseado
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repo.create_partial_movement(non_existent_game_id, non_existent_player_id, non_existent_card_id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"

@pytest.mark.integration_test
def test_create_partial_movement_no_player(partial_movement_repo, session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.commit()
    
    non_existent_player_id = 9999
    non_existent_card_id = 9999
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar el jugador deseado
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repo.create_partial_movement(game.id, non_existent_player_id, non_existent_card_id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found in the specified game"
    
@pytest.mark.integration_test
def test_create_partial_movement_player_not_in_game(partial_movement_repo, session):
    game = Game(name='my game', min_players=2, max_players=3)
    session.add(game)
    session.commit()
    
    player_game = Game(name='player game', min_players=2, max_players=3)
    session.add(player_game)
    session.commit()
    
    game_state = GameState(game_id = player_game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player1", game_id=player_game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()
    
    non_existent_card_id = 9999
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar el jugador deseado
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repo.create_partial_movement(game.id, player.id, non_existent_card_id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found in the specified game"

@pytest.mark.integration_test
def test_create_partial_movement_card_not_in_player_hand(partial_movement_repo, session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player1)
    session.commit()
    
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player2)
    session.commit()
    
    card = MovementCard(player_id = player2.id ,game_id=game.id,type=typeEnum.DIAGONAL_CONT, description = '', used= False)
    session.add(card)
    session.commit()
    
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar la carta
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repo.create_partial_movement(game.id, player1.id, card.id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Card not found for the specified player and game" 


@pytest.mark.integration_test
def test_undo_movement(partial_movement_repo: PartialMovementRepository, session):
    # agrego un movimiento parcial
    partial_mov = PartialMovements(
        pos_from_x = 0,
        pos_from_y = 0,
        pos_to_x = 1,
        pos_to_y = 1, 
        game_id = 1,
        player_id = 1,
        mov_card_id = 1
    )

    session.add(partial_mov)
    session.commit()
    
    N_partial_movement = session.query(PartialMovements).count()

    # agarro el ultimo por id
    last_partial_movement_in_db = session.query(PartialMovements).order_by(PartialMovements.id.desc()).first()

    partial_movement_deleted = partial_movement_repo.undo_movement(1,1,session)

    # me fijo que en efecto se haya borrado 
    assert N_partial_movement - 1 == session.query(PartialMovements).count() 
    assert last_partial_movement_in_db.id == partial_movement_deleted.id
    assert partial_mov.mov_card_id == partial_movement_deleted.mov_card_id


@pytest.mark.integration_test
def test_undo_inexistent_movement(partial_movement_repo: PartialMovementRepository, session):
    # me fijo que no haya nada
    # assert session.query(PartialMovementRepository).count() == 0
    
    with pytest.raises(HTTPException) as excinfo:
        partial_movement_repo.undo_movement(532,6,session)
    
    assert excinfo.value.status_code == 404
    assert "There is no partial movement to undo" in str(excinfo.value.detail)

@pytest.mark.integration_test
def test_return_partial_movements_by_player(partial_movement_repo, setup_game_player_card, session):
    game, player, card = setup_game_player_card

    # agrego movimientos parciales
    
    partial_mov1 = PartialMovements(
        pos_from_x = 0,
        pos_from_y = 0,
        pos_to_x = 1,
        pos_to_y = 1, 
        game_id = game.id,
        player_id = player.id,
        mov_card_id = 1
    )
    partial_mov2 = PartialMovements(
        pos_from_x = 1,
        pos_from_y = 1,
        pos_to_x = 2,
        pos_to_y = 2, 
        game_id = game.id,
        player_id = player.id,
        mov_card_id = 2
    )
    
    session.add(partial_mov1)
    session.add(partial_mov2)
    session.commit()
    
    partial_movements = partial_movement_repo.return_partial_movements_by_player(game.id, player.id, session)
    assert len(partial_movements) == 2
    assert partial_movements[0].mov_card_id == 1
    assert partial_movements[1].mov_card_id == 2
    

@pytest.mark.integration_test
def test_return_partial_movements_by_player_mov_not_found(partial_movement_repo, session):
    game_id = 999
    player_id = 999
    partial_movements = partial_movement_repo.return_partial_movements_by_player(game_id, player_id, session)
    
    assert partial_movements == []


@pytest.mark.integration_test
def test_undo_movement_by_id(partial_movement_repo, setup_game_player_card, session):
    game, player, card = setup_game_player_card

    # agrego movimientos parciales
    
    partial_mov = PartialMovements(
        pos_from_x = 0,
        pos_from_y = 0,
        pos_to_x = 1,
        pos_to_y = 1, 
        game_id = game.id,
        player_id = player.id,
        mov_card_id = 1
    )

    session.add(partial_mov)
    session.commit()
    N_partial_movement = session.query(PartialMovements).count()
    partial_movement_repo.undo_movement_by_id(partial_mov.id, session)
    # me fijo que en efecto se haya borrado 
    assert N_partial_movement - 1 == session.query(PartialMovements).count()

@pytest.mark.integration_test
def test_undo_inexistent_movement_by_id(partial_movement_repo, session):
    with pytest.raises(HTTPException) as excinfo:
        partial_movement_repo.undo_movement_by_id(999, session)
    
    assert excinfo.value.status_code == 404
    assert "Partial movement not found" in str(excinfo.value.detail)

@pytest.mark.integration_test
def test_delete_all_partial_movements_by_player(partial_movement_repo: PartialMovementRepository, setup_game_player_card, session: Session):
    game, player, card = setup_game_player_card

    partial_mov1 = PartialMovements(
        pos_from_x=0,
        pos_from_y=0,
        pos_to_x=1,
        pos_to_y=1,
        game_id=game.id,
        player_id=player.id,
        mov_card_id=1
    )
    partial_mov2 = PartialMovements(
        pos_from_x=1,
        pos_from_y=1,
        pos_to_x=2,
        pos_to_y=2,
        game_id=game.id,
        player_id=player.id,
        mov_card_id=2
    )

    session.add(partial_mov1)
    session.add(partial_mov2)
    session.commit()

    assert session.query(PartialMovements).filter_by(player_id=player.id).count() == 2

    partial_movement_repo.delete_all_partial_movements_by_player(player.id, session)

    assert session.query(PartialMovements).filter_by(player_id=player.id).count() == 0
