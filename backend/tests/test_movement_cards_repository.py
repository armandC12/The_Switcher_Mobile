import pdb
import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound

from fastapi import HTTPException

from movementCards.movement_cards_repository import MovementCardsRepository
from game.models import Game
from gameState.models import GameState, StateEnum
from movementCards.models import MovementCard, typeEnum
from movementCards.schemas import MovementCardOut
from player.models import Player
from fastapi import HTTPException

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture
def movement_cards_repository():
    return MovementCardsRepository()

@pytest.mark.integration_test
def test_get_players_movement_cards(movement_cards_repository: MovementCardsRepository, session):
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1, 
                                                MovementCard.player_id.is_not(None)).count()

    list_of_cards = movement_cards_repository.get_players_movement_cards(1, session)
    
    assert len(list_of_cards) == N_cards
    
@pytest.mark.integration_test
def test_get_players_movement_cards_no_cards(movement_cards_repository: MovementCardsRepository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_players_movement_cards(game.id, session)

    assert excinfo.value.status_code == 404
    assert "There no movement cards associated with this game" in str(excinfo.value.detail)

@pytest.mark.integration_test
def test_get_players_movement_cards_no_game(movement_cards_repository: MovementCardsRepository, session):
    nonexistent__game_id = 213363565
    
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_players_movement_cards(nonexistent__game_id, session)

    assert excinfo.value.status_code == 404
    assert "Game not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_movement_cards(movement_cards_repository: MovementCardsRepository, session):
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1, 
                                                MovementCard.player_id == 1).count()

    list_of_cards = movement_cards_repository.get_movement_cards(1, 1, session)
    
    assert len(list_of_cards) == N_cards


@pytest.mark.integration_test
def test_get_movement_cards_no_cards(movement_cards_repository: MovementCardsRepository, session):
    # uso un game_id y player_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_movement_cards(999, 999, session)
    
    assert excinfo.value.status_code == 404
    assert "There no movement cards associated with this game and player" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_movement_card_by_id(movement_cards_repository: MovementCardsRepository, session):
    # busco la cantidad de cartas con todos id 1
    test_card = session.query(MovementCard).filter(MovementCard.game_id == 1,
                                            MovementCard.player_id == 1,
                                            MovementCard.id == 1).one()
        
    movement_card = movement_cards_repository.get_movement_card_by_id(1, 1, 1, session)
        
    assert test_card.id == movement_card.id


@pytest.mark.integration_test
def test_get_movement_card_by_id_not_found(movement_cards_repository: MovementCardsRepository, session):
    # uso un mov_card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_movement_card_by_id(1, 1, 999, session)
    
    assert excinfo.value.status_code == 404
    assert "Movement card not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_create_new_movement_card(movement_cards_repository: MovementCardsRepository, session):
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1).count()
    
    movement_cards_repository.create_movement_card(1, typeEnum.EN_L_DER,1, session)
    
    assert session.query(MovementCard).filter(MovementCard.game_id == 1).count() == N_cards + 1

    
@pytest.mark.integration_test
def test_grab_mov_cards(movement_cards_repository: MovementCardsRepository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)
    session.add_all([player1, player2])
    session.commit()
    
    session.add_all([
        MovementCard(player_id = player1.id ,game_id=game.id,type=typeEnum.DIAGONAL_CONT, description = '', used= False),
        MovementCard(player_id = player1.id , game_id=game.id, type=typeEnum.EN_L_DER, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_ESP, description = '', used= False , position = 1),
        MovementCard(player_id = player2.id , game_id=game.id, type=typeEnum.LINEAL_AL_LAT, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= False, position = 0),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_ESP, description = '', used= False, position = 2),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_CONT, description = '', used= False, position = 3),
        MovementCard(game_id=game.id, type=typeEnum.EN_L_IZQ, description = '', used= False, position = 5),
        MovementCard(game_id=game.id, type=typeEnum.EN_L_IZQ, description = '', used= False, position = 4)
    ])
    session.commit()
    
    movement_cards_repository.grab_mov_cards(player1.id, game.id, session)
    movement_cards_repository.grab_mov_cards(player2.id, game.id, session)

    shown_cards_player1 = session.query(MovementCard).filter(
        MovementCard.player_id == player1.id,
        MovementCard.game_id == game.id,
    ).all()
    
    shown_cards_player2 = session.query(MovementCard).filter(
        MovementCard.player_id == player2.id,
        MovementCard.game_id == game.id,
    ).all()
    
    cards_left = session.query(MovementCard).filter(
        MovementCard.game_id == game.id,
        MovementCard.player_id.is_(None),
        MovementCard.used == False
    ).all()
    
    assert len(shown_cards_player1) == 3
    for card in shown_cards_player1:
        assert card.position == None
        
    assert len(shown_cards_player2) == 3
    for card in shown_cards_player2:
        assert card.position == None
        assert card.type in [typeEnum.LINEAL_ESP, typeEnum.LINEAL_AL_LAT, typeEnum.DIAGONAL_ESP]
    
    positions_left = {card.position for card in cards_left}
    assert positions_left == {3, 4, 5}
    
@pytest.mark.integration_test
def test_grab_mov_cards_no_game(movement_cards_repository: MovementCardsRepository, session):
    
    game_id = 45363
    player_id = 1
    
    with pytest.raises(HTTPException) as exc_info:
        movement_cards_repository.grab_mov_cards(player_id, game_id, session)

    # Verificar que la excepción HTTP tiene el código de estado correcto
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No game found"
    
@pytest.mark.integration_test
def test_grab_mov_cards_no_player(movement_cards_repository: MovementCardsRepository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)
    session.add_all([player1, player2])
    session.commit()
    
    player_id = 123141
    
    with pytest.raises(HTTPException) as exc_info:
        movement_cards_repository.grab_mov_cards(player_id, game.id, session)

    # Verificar que la excepción HTTP tiene el código de estado correcto
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found"
    
    
@pytest.mark.integration_test
def test_grab_mov_cards_and_reshuffle(movement_cards_repository: MovementCardsRepository, session):
    
    game = Game(name="Grab and Reshuffle Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)
    session.add_all([player1, player2])
    session.commit()
    
    session.add_all([
        MovementCard(player_id = player1.id ,game_id=game.id,type=typeEnum.DIAGONAL_CONT, description = '', used= False),
        MovementCard(player_id = player1.id , game_id=game.id, type=typeEnum.EN_L_DER, description = '', used= False),
        MovementCard(player_id = player1.id , game_id=game.id, type=typeEnum.EN_L_DER, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= True),
        MovementCard(player_id = player2.id , game_id=game.id, type=typeEnum.LINEAL_AL_LAT, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= True),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= True),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_CONT, description = '', used= True),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= True),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_ESP, description = '', used= True)
    ])
    session.commit()
    
    movement_cards_repository.grab_mov_cards(player1.id, game.id, session)
    movement_cards_repository.grab_mov_cards(player2.id, game.id, session)

    shown_cards_player1 = session.query(MovementCard).filter(
        MovementCard.player_id == player1.id,
        MovementCard.game_id == game.id,
    ).all()
    
    shown_cards_player2 = session.query(MovementCard).filter(
        MovementCard.player_id == player2.id,
        MovementCard.game_id == game.id,
    ).all()
    
    cards_left = session.query(MovementCard).filter(
        MovementCard.game_id == game.id,
        MovementCard.player_id.is_(None),
        MovementCard.used == False
    ).all()
    
    assert len(shown_cards_player1) == 3
    assert len(shown_cards_player2) == 3
    assert len(cards_left) == 4
    
    positions_left = {card.position for card in cards_left}
    assert positions_left == {2, 3, 4, 5}


@pytest.mark.integration_test
def test_reshuffle_movement_deck(movement_cards_repository: MovementCardsRepository, session):
    # Crear un juego y agregarlo a la sesión
    game = Game(name="My Game", max_players=3, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)
    session.add_all([player1, player2])
    session.commit()

    # Agregar cartas de movimiento usadas y no usadas al juego
    session.add_all([
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description='', used=True),
        MovementCard(game_id=game.id, type=typeEnum.EN_L_DER, description='', used=True),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_AL_LAT, description='', used=False, position = 7),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description='', used=True),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_CONT, description='', used=True),
        MovementCard(player_id = player1.id, game_id=game.id, type=typeEnum.LINEAL_CONT, description='', used=False),
        MovementCard(player_id = player1.id, game_id=game.id, type=typeEnum.LINEAL_CONT, description='', used=False),
        MovementCard(player_id = player2.id, game_id=game.id, type=typeEnum.LINEAL_CONT, description='', used=False),
    ])
    session.commit()

    # Llamar al método reshuffle_movement_deck
    movement_cards_repository.reshuffle_movement_deck(game.id, session)
    
    # Verificar que todas las cartas usadas ahora est
    # án marcadas como no usadas
    used_cards_after_reshuffle = session.query(MovementCard).filter(
        MovementCard.game_id == game.id,
        MovementCard.player_id.is_(None),
        MovementCard.used == True
    ).all()

    assert len(used_cards_after_reshuffle) == 0

    unused_cards_after_reshuffle = session.query(MovementCard).filter(
        MovementCard.game_id == game.id,
        MovementCard.player_id.is_(None),
        MovementCard.used == False
    ).all()
    
    assert len(unused_cards_after_reshuffle) == 5
    positions_left = {card.position for card in unused_cards_after_reshuffle}
    assert positions_left == {0, 1, 2, 3, 4}


@pytest.mark.integration_test
def test_reshuffle_movement_deck_no_used_cards(movement_cards_repository: MovementCardsRepository, session):
    # Crear un juego y agregarlo a la sesión
    game = Game(name="Test Game", max_players=3, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)
    session.add_all([player1, player2])
    session.commit()

    # Agregar cartas de movimiento no usadas al juego
    session.add_all([
        MovementCard(player_id = player1.id, game_id=game.id, type=typeEnum.LINEAL_CONT, description='', used=False),
        MovementCard(player_id = player1.id, game_id=game.id, type=typeEnum.LINEAL_CONT, description='', used=False),
        MovementCard(player_id = player2.id, game_id=game.id, type=typeEnum.LINEAL_CONT, description='', used=False),
    ])
    session.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.reshuffle_movement_deck(game.id, session)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "No used cards available to reshuffle"


@pytest.mark.integration_test
def test_create_movement_card_invalid_type(movement_cards_repository: MovementCardsRepository, session):
    # Cuento cuantas cartas tiene el game 1 antes de crear una nueva carta
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1).count()

    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.create_movement_card(1, "INVALID_TYPE", 1, session)

    # Me fijo que no se haya creado ninguna carta de movimiento
    assert session.query(MovementCard).filter(MovementCard.game_id == 1).count() == N_cards
    assert excinfo.value.status_code == 400 # Me fijo que de BAD REQUEST
    assert "Incorrect type for movement card: INVALID_TYPE" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_create_movement_card_with_invalid_game_id(movement_cards_repository: MovementCardsRepository, session):
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.create_movement_card(-1, typeEnum.EN_L_DER, 1, session)

    assert excinfo.value.status_code == 404


@pytest.mark.integration_test
def test_get_movement_cards_deck(movement_cards_repository: MovementCardsRepository, session):
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1, 
                                                 MovementCard.player_id.is_(None)).count()

    movement_deck = movement_cards_repository.get_movement_deck(1, session)

    assert N_cards == len(movement_deck)


@pytest.mark.integration_test
def test_get_movement_deck_no_cards(movement_cards_repository: MovementCardsRepository, session):
    # uso un game_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_movement_deck(999, session)
    
    assert excinfo.value.status_code == 404
    assert "There no movement cards associated with this game" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_assign_mov_card(movement_cards_repository: MovementCardsRepository, session):
    # busco la primer carta de movimiento que encuentre que no tenga un player asignado
    test_card = session.query(MovementCard).filter(MovementCard.player_id == None).first()

    # Le asigno el player 1 a la carta
    movement_cards_repository.assign_mov_card(test_card.id, 1, session)

    
    assert test_card.player_id == 1
    assert test_card.used == False # Me aseguro que la flag used no haya sido cambiada


@pytest.mark.integration_test
def test_discard_mov_card(movement_cards_repository: MovementCardsRepository, session):
    # busco la carta de movimiento con id 1 que se que tiene al player 1
    test_card = session.query(MovementCard).filter(MovementCard.id == 1).one()
    
    # Le asigno el player 1 a la carta
    movement_cards_repository.discard_mov_card(test_card.id, session)

    
    assert test_card.player_id == None # Me fijo que la carta no tenga mas duenio
    assert test_card.used == True # Me fijo que la carta esta como usada
    assert test_card.position == None # Me fijo que la position sea None


# dejar este test debajo del discard_mov_card, asi se descarta la unica carta sin player y no da error la query
@pytest.mark.integration_test
def test_assign_mov_card_invalid_player(movement_cards_repository: MovementCardsRepository, session):
    # busco la primer carta de movimiento que encuentre que no tenga un player asignado
    test_card = session.query(MovementCard).filter(MovementCard.player_id == None).first()

    # uso un player_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.assign_mov_card(test_card.id, 999, session)
    
    assert excinfo.value.status_code == 404
    assert "no player with specified id" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_assign_mov_card_invalid_card(movement_cards_repository: MovementCardsRepository, session):
    # uso un mov_card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.assign_mov_card(999, 1, session)

    assert excinfo.value.status_code == 404
    assert "There no movement cards associated with this game" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_discard_mov_card_invalid_card(movement_cards_repository: MovementCardsRepository, session):
    # uso un mov_card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.discard_mov_card(999, session)

    assert excinfo.value.status_code == 404
    assert f"There no movement cards associated with this id 999" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_mark_card_partially_used(movement_cards_repository, session):
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


    # Marco carta como parcialmente usada
    movement_cards_repository.mark_card_partially_used(card.id, session)

    # Verifico
    updated_card = session.query(MovementCard).filter_by(id=card.id).one()
    assert updated_card.used is True

    
@pytest.mark.integration_test
def test_mark_card_partially_used_not_found(movement_cards_repository, session):
    non_existent_card_id = 9999

    # Llamo con un id de una carta que no existe
    with pytest.raises(HTTPException) as exc_info:
        movement_cards_repository.mark_card_partially_used(non_existent_card_id, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No movement card found"

@pytest.mark.integration_test
def test_mark_card_in_player_hand(movement_cards_repository, session):
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


    # Marco carta como en mano del jugador
    movement_cards_repository.mark_card_in_player_hand(card.id, session)

    # Verifico
    updated_card = session.query(MovementCard).filter_by(id=card.id).one()
    assert updated_card.used is False
    
@pytest.mark.integration_test
def test_mark_card_in_player_hand_not_found(movement_cards_repository, session):
    non_existent_card_id = 9999

    # Llamo con un id de una carta que no existe
    with pytest.raises(HTTPException) as exc_info:
        movement_cards_repository.mark_card_in_player_hand(non_existent_card_id, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No movement card found"


@pytest.mark.integration_test
def test_get_movement_card_type(movement_cards_repository: MovementCardsRepository, session):
    card_id = 1
    mov_card = session.query(MovementCard).filter(MovementCard.id == card_id).one()
    type = typeEnum(mov_card.type)

    movement_type = movement_cards_repository.get_movement_card_type(card_id, session)

    assert type == movement_type


@pytest.mark.integration_test
def test_get_movement_card_type_card_not_found(movement_cards_repository: MovementCardsRepository, session):
    card_id = 999
    # uso un card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_movement_card_type(card_id, session)
    
    assert excinfo.value.status_code == 404
    assert "No movement card found" in str(excinfo.value.detail)
    
    
@pytest.mark.integration_test
def test_discard_all_player_partially_used_cards(movement_cards_repository: MovementCardsRepository, session: Session):
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()

    partially_used_card1 = MovementCard(player_id=player.id, game_id=game.id, type=typeEnum.DIAGONAL_CONT, description='', used=True)
    partially_used_card2 = MovementCard(player_id=player.id, game_id=game.id, type=typeEnum.EN_L_DER, description='', used=True)
    session.add_all([partially_used_card1, partially_used_card2])
    session.commit()
    
    #pdb.set_trace()

    movement_cards_repository.discard_all_player_partially_used_cards(player.id, session)

    discarded_cards = session.query(MovementCard).filter(
        MovementCard.player_id == player.id,
        MovementCard.used == True
    ).all()

    assert len(discarded_cards) == 0

    discarded_cards = session.query(MovementCard).filter(
        MovementCard.used == True,
        MovementCard.game_id == game.id
    ).all()

    for card in discarded_cards:
        assert card.player_id is None
        assert card.position is None
        
