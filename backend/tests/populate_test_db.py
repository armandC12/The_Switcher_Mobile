import random
from database.db import SessionLocal, engine, init_db
from sqlalchemy.orm import sessionmaker, Session
from board.models import Box, Board, ColorEnum
from figureCards.models import FigureCard, DifficultyEnum, typeEnum as figTypeEnum
from game.models import Game
from gameState.models import GameState, StateEnum
from movementCards.models import MovementCard, typeEnum as movTypeEnum
from player.models import Player, turnEnum



def create_game(name, min_players, max_players, session):
    game = Game(name=name, min_players=min_players, max_players=max_players)
    session.add(game)
    # session.flush()
    session.commit()
    return game

def create_game_state(game, state, session):
    game_state = GameState(state=state, game_id=game.id)
    session.add(game_state)
    # session.flush()
    session.commit()
    return game_state

def create_player(name, game, game_state, turn, host, session):
    player = Player(name=name, game_id=game.id, game_state_id=game_state.id, turn=turn, host=host, winner=False)
    session.add(player)
    # session.flush()
    session.commit()

    return player

def create_board(game, session):
    board = Board(game_id=game.id)
    session.add(board)
    # session.flush()
    session.commit()

    return board

def create_box(color, pos_x, pos_y, game, board, session):
    box = Box(color=color, pos_x=pos_x, pos_y=pos_y, game_id=game.id, board_id=board.id, highlight= False)
    session.add(box)
    # session.flush()
    session.commit()

    return box

def create_movement_card(description, used, player, game, type, session):
    card = MovementCard(description=description, used=used, player_id=player.id, game_id=game.id, type=type)
    session.add(card)
    # session.flush()
    session.commit()

    return card

def create_figure_card(show, difficulty, player, type, game, blocked, soft_blocked, session):
    card = FigureCard(show=show, difficulty=difficulty, player_id=player.id, type=type, game_id=game.id, blocked=blocked, soft_blocked=soft_blocked)
    session.add(card)
    # session.flush()
    session.commit()

    return card

# Populate the database with sample data
def populate_database():
    session = SessionLocal()
    try:
        # Create a game
        game = create_game("Test Game", 2, 4, session)

        # Create game state
        game_state = create_game_state(game, StateEnum.WAITING, session)

        # Create players
        players = [
            create_player(f"Player {i}", game, game_state, turn, i == 0, session)
            for i, turn in enumerate([turnEnum.PRIMERO, turnEnum.SEGUNDO, turnEnum.TERCERO, turnEnum.CUARTO])
        ]

        # Set current player
        game_state.current_player = players[0].id

        # Create board
        board = create_board(game, session)

        # Create boxes
        colors = list(ColorEnum)
        for x in range(6):
            for y in range(6):
                create_box(random.choice(colors), x, y, game, board, session)

        # Create movement cards
        movements = ["Descripcion 1", "Descripcion 2", "Descripcion 3", "Descripcion 4"]
        for player in players:
            for _ in range(3):
                create_movement_card(random.choice(movements), False, player, game, random.choice(list(movTypeEnum)), session)

        # Create figure cards
        for player in players:
            for _ in range(3):
                create_figure_card(False, random.choice(list(DifficultyEnum)), player, random.choice(list(figTypeEnum)), game, False,False, session)

        # Commit the session
        session.commit()
    except Exception as e:
        print(f"An error ocurred: {e}")
        session.rollback()
        
if __name__ == "__main__":
    init_db()
    Session = sessionmaker(bind=engine)
    populate_database()
    print("Database populated with test data.")