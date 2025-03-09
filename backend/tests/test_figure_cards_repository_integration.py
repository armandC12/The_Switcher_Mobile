import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from figureCards.figure_cards_repository import FigureCardsRepository
from board.models import  Board, Box
from figureCards.models import FigureCard, typeEnum
from game.models import Game
from gameState.models import GameState, StateEnum
from movementCards.models import MovementCard
from player.models import Player
from fastapi import HTTPException


from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def figure_cards_repository():
    return FigureCardsRepository()


@pytest.mark.integration_test
def test_get_figure_cards(figure_cards_repository: FigureCardsRepository, session):
    game_id = 1
    player_id = 1
    N_cards = session.query(FigureCard).filter(FigureCard.game_id == game_id, 
                                                FigureCard.player_id == player_id).count()
    
    list_of_cards = figure_cards_repository.get_figure_cards(game_id, player_id, session)
    
    assert len(list_of_cards) == N_cards


@pytest.mark.integration_test
def test_get_figure_card_by_id(figure_cards_repository: FigureCardsRepository, session):
    game_id = 1
    player_id = 1
    figure_card_id = 1
    try:
        # busco la cantidad de cartas con todos id 1
        test_card = session.query(FigureCard).filter(FigureCard.game_id == game_id,
                                                  FigureCard.player_id == player_id,
                                                  FigureCard.id == figure_card_id).one()
        
        figure_card = figure_cards_repository.get_figure_card_by_id(game_id, player_id, figure_card_id, session)

        assert test_card.id == figure_card.id
    except NoResultFound:
        raise ValueError("There is no figure card with game_id=1, player_id=1 and id=1")


@pytest.mark.integration_test
def test_get_figure_card_by_id_not_found(figure_cards_repository: FigureCardsRepository, session):
    # uso un figure_card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        figure_cards_repository.get_figure_card_by_id(1, 1, 999, session)
    
    assert excinfo.value.status_code == 404
    assert "Figure card not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_figure_cards_no_cards(figure_cards_repository: FigureCardsRepository, session):
    game_id = 1
    player_id = 999
    
    list_of_cards = figure_cards_repository.get_figure_cards(game_id, player_id, session)
    
    assert len(list_of_cards) == 0


@pytest.mark.integration_test
def test_create_new_figure_card(figure_cards_repository: FigureCardsRepository, session):
    N_cards = session.query(FigureCard).filter(FigureCard.game_id == 1,
                                               FigureCard.player_id == 1).count()

    
    figure_cards_repository.create_figure_card(1, 1, typeEnum.FIG04, True, False, session)
    
    assert session.query(FigureCard).filter(FigureCard.player_id == 1).count() == N_cards + 1
    

@pytest.mark.integration_test
def test_grab_figure_cards(figure_cards_repository, session):
    
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
        FigureCard(player_id=player1.id, game_id=game.id, show=True, blocked=False, soft_blocked=False,type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player2.id, game_id=game.id, show=True, blocked=False, soft_blocked=False,type=typeEnum.FIG02)
    ])
    session.commit()
    
    figure_cards_repository.grab_figure_cards(player1.id, game.id, session)

    shown_cards_player1 = session.query(FigureCard).filter(
        FigureCard.player_id == player1.id,
        FigureCard.game_id == game.id,
        FigureCard.show == True
    ).all()
    
    assert len(shown_cards_player1) == 3
    

@pytest.mark.integration_test
def test_grab_figure_cards_none_needed(figure_cards_repository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add_all([player1])
    session.commit()
    
    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, show=True, blocked=False, soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, blocked=False, soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, blocked=False, soft_blocked=False, type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False,  type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False,  type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False,  type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False,  type=typeEnum.FIG01),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, blocked=False,soft_blocked=False,  type=typeEnum.FIG01),
    ])
    session.commit()
    
    figure_cards_repository.grab_figure_cards(player1.id, game.id, session)

    shown_cards_player1 = session.query(FigureCard).filter(
        FigureCard.player_id == player1.id,
        FigureCard.game_id == game.id,
        FigureCard.show == True
    ).all()
    #Reviso que el jugador no obtuvo mas cartas del mazo
    assert len(shown_cards_player1) == 3
    
@pytest.mark.integration_test
def test_grab_figure_cards_needed_but_one_blocked(figure_cards_repository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add_all([player1])
    session.commit()
    
    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01 , blocked = False, soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = True  , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
    ])
    session.commit()
    
    figure_cards_repository.grab_figure_cards(player1.id, game.id, session)

    shown_cards_player1 = session.query(FigureCard).filter(
        FigureCard.player_id == player1.id,
        FigureCard.game_id == game.id,
        FigureCard.show == True
    ).all()
    #Reviso que el jugador no obtuvo mas cartas del mazo
    assert len(shown_cards_player1) == 2

@pytest.mark.integration_test
def test_grab_figure_cards_not_needed_and_one_blocked(figure_cards_repository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add_all([player1])
    session.commit()
    
    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = True ,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
    ])
    session.commit()
    
    figure_cards_repository.grab_figure_cards(player1.id, game.id, session)

    shown_cards_player1 = session.query(FigureCard).filter(
        FigureCard.player_id == player1.id,
        FigureCard.game_id == game.id,
        FigureCard.show == True
    ).all()
    #Reviso que el jugador no obtuvo mas cartas del mazo
    assert len(shown_cards_player1) == 3
    
@pytest.mark.integration_test
def test_grab_figure_cards_needed_but_one_soft_blocked(figure_cards_repository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add_all([player1])
    session.commit()
    
    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False , soft_blocked=True),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01 , blocked = False, soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False  , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
    ])
    session.commit()
    
    figure_cards_repository.grab_figure_cards(player1.id, game.id, session)

    shown_cards_player1 = session.query(FigureCard).filter(
        FigureCard.player_id == player1.id,
        FigureCard.game_id == game.id,
        FigureCard.show == True
    ).all()
    #Reviso que el jugador no obtuvo mas cartas del mazo
    assert len(shown_cards_player1) == 2

@pytest.mark.integration_test
def test_grab_figure_cards_not_needed_and_one_soft_blocked(figure_cards_repository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add_all([player1])
    session.commit()
    
    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False,soft_blocked=True),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False ,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False,soft_blocked=False),
    ])
    session.commit()
    
    figure_cards_repository.grab_figure_cards(player1.id, game.id, session)

    shown_cards_player1 = session.query(FigureCard).filter(
        FigureCard.player_id == player1.id,
        FigureCard.game_id == game.id,
        FigureCard.show == True
    ).all()
    #Reviso que el jugador no obtuvo mas cartas del mazo
    assert len(shown_cards_player1) == 3
    

@pytest.mark.integration_test
def test_grab_figure_cards_this_should_never_happen(figure_cards_repository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add_all([player1])
    session.commit()
    
    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01 , blocked = False, soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=True, type=typeEnum.FIG01 , blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = True  , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, show=False, type=typeEnum.FIG01, blocked = False , soft_blocked=False),
    ])
    session.commit()
    
    figure_cards_repository.grab_figure_cards(player1.id, game.id, session)

    shown_cards_player1 = session.query(FigureCard).filter(
        FigureCard.player_id == player1.id,
        FigureCard.game_id == game.id,
        FigureCard.show == True
    ).all()
    
    
    assert len(shown_cards_player1) == 3

@pytest.mark.integration_test
def test_grab_figure_cards_no_player(figure_cards_repository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    #le paso un id de un jugador que no existe en la db de test
    player_id = 7643868
    
    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.grab_figure_cards(player_id, game.id, session)
    
    # Verificar que la excepción HTTP tiene el código de estado correcto
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found in the game"


@pytest.mark.integration_test
def test_grab_figure_cards_no_game(figure_cards_repository, session):
    
    #le paso un id de un jugador que no existe en la db de test
    game_id = 843565
    #le paso un id de un jugador cq
    player_id = 6
    
    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.grab_figure_cards(player_id, game_id, session)
    
    # Verificar que la excepción HTTP tiene el código de estado correcto
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No game found"


@pytest.mark.integration_test
def test_discard_figure_card(figure_cards_repository, session):
    game_id = 1
    player_id = 1
    figure_card_id = 1
    N_cards = session.query(FigureCard).filter(FigureCard.game_id == game_id, 
                                                FigureCard.player_id == player_id).count()
    
    response = figure_cards_repository.discard_figure_card(figure_card_id, session)
    

    assert N_cards - 1 == session.query(FigureCard).filter(FigureCard.game_id == game_id, 
                                                           FigureCard.player_id == player_id).count()
    
    assert response == {"message": "The figure cards was successfully discarded"}


@pytest.mark.integration_test
def test_discard_inexistent_figure_card(figure_cards_repository, session):
    figure_card_id = 999
    
    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.discard_figure_card(figure_card_id, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"There no figure card associated with this id {figure_card_id}"


@pytest.mark.integration_test
def test_unblock_figure_card(figure_cards_repository: FigureCardsRepository, session):
    game = Game(name="My Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()

    figure_card = FigureCard(player_id=player.id, game_id=game.id, type=typeEnum.FIG01, show=True, blocked=True, soft_blocked=False)
    session.add(figure_card)
    session.commit()

    response = figure_cards_repository.unblock_figure_card(figure_card.id, session)

    assert response == {"message": "The figure card was successfully unblocked"}

    unblocked_card = session.query(FigureCard).filter(FigureCard.id == figure_card.id).one()
    assert unblocked_card.blocked == False


@pytest.mark.integration_test
def test_unblock_figure_card_not_found(figure_cards_repository: FigureCardsRepository, session):
    game = Game(name="My Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.unblock_figure_card(999, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Figure card not found"
    
@pytest.mark.integration_test
def test_soft_block_figure_card(figure_cards_repository: FigureCardsRepository, session):
    game = Game(name="My Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()

    figure_card = FigureCard(player_id=player.id, game_id=game.id, type=typeEnum.FIG01, show=True, blocked=False, soft_blocked=False)
    session.add(figure_card)
    session.commit()

    figure_cards_repository.soft_block_figure_card(figure_card.id, session)


    unblocked_card = session.query(FigureCard).filter(FigureCard.id == figure_card.id).one()
    assert unblocked_card.soft_blocked == True


@pytest.mark.integration_test
def test_soft_block_figure_card_not_found(figure_cards_repository: FigureCardsRepository, session):
    game = Game(name="My Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.soft_block_figure_card(999, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Figure card not found"

@pytest.mark.integration_test
def test_block_figure_card(figure_cards_repository, session):
    game_id = 1
    figure_card_id = 2

    unblocked_card = session.query(FigureCard).filter(FigureCard.game_id == game_id, 
                                                FigureCard.id == figure_card_id).one()
    
    unblocked = unblocked_card.blocked
    response = figure_cards_repository.block_figure_card(game_id, figure_card_id, session)

    blocked_card = session.query(FigureCard).filter(FigureCard.game_id == game_id, 
                                                FigureCard.id == figure_card_id).one()
    
    # me fijo que sus valores de blocked sean distintos
    assert unblocked != blocked_card.blocked
    assert response == {"message": "The figure cards was successfully blocked"}


@pytest.mark.integration_test
def test_block_inexistent_figure_card(figure_cards_repository, session):
    game_id = 1
    figure_card_id = 999
    
    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.block_figure_card(game_id, figure_card_id, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"There no figure card associated with id {figure_card_id} in game {game_id}"

@pytest.mark.integration_test
def test_fetch_shown_figure_card_types(figure_cards_repository: FigureCardsRepository, session):
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)

    session.add(player1)
    session.add(player2)
    session.commit()

    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, type=typeEnum.FIG01, show=True, blocked=False, soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, type=typeEnum.FIG02, show=True, blocked=False, soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, type=typeEnum.FIG03, show=True, blocked=False, soft_blocked=False),
        FigureCard(player_id=player2.id, game_id=game.id, type=typeEnum.FIG04, show=True, blocked=True , soft_blocked=False),
        FigureCard(player_id=player2.id, game_id=game.id, type=typeEnum.FIG05, show=True, blocked=False, soft_blocked=False)
    ])
    session.commit()

    # Call the method to fetch shown figure card types
    result = figure_cards_repository.fetch_shown_figure_card_types(game.id, session)

    # Assert the result
    assert sorted(result) == sorted([typeEnum.FIG01, typeEnum.FIG02, typeEnum.FIG03, typeEnum.FIG05])


@pytest.mark.integration_test
def test_fetch_shown_figure_card_types_no_duplicates(figure_cards_repository: FigureCardsRepository, session):
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)

    session.add(player1)
    session.add(player2)
    session.commit()

    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, type=typeEnum.FIG01, show=True, blocked=False, soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, type=typeEnum.FIG02, show=True, blocked=False, soft_blocked=False),
        FigureCard(player_id=player1.id, game_id=game.id, type=typeEnum.FIG03, show=True, blocked=False, soft_blocked=False),
        FigureCard(player_id=player2.id, game_id=game.id, type=typeEnum.FIG04, show=True, blocked=False, soft_blocked=False),
        FigureCard(player_id=player2.id, game_id=game.id, type=typeEnum.FIG04, show=True, blocked=False, soft_blocked=False)
    ])
    session.commit()

    # Call the method to fetch shown figure card types
    result = figure_cards_repository.fetch_shown_figure_card_types(game.id, session)

    # Assert the result
    assert sorted(result) == sorted([typeEnum.FIG01, typeEnum.FIG02, typeEnum.FIG03, typeEnum.FIG04])


@pytest.mark.integration_test
def test_fetch_shown_figure_card_types_no_shown_cards(figure_cards_repository: FigureCardsRepository, session):
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()

    game_state = GameState(game_id=game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)

    session.add(player1)
    session.add(player2)

    session.commit()

    session.add_all([
        FigureCard(player_id=player1.id, game_id=game.id, type=typeEnum.FIG01, show=False, blocked=False, soft_blocked=False),
        FigureCard(player_id=player2.id, game_id=game.id, type=typeEnum.FIG02, show=False, blocked=False, soft_blocked=False),
    ])
    session.commit()

    result = figure_cards_repository.fetch_shown_figure_card_types(game.id, session)

    assert result == []