from time import sleep
from fastapi import APIRouter, Depends,status, BackgroundTasks
from sqlalchemy.orm import Session
from database.db import get_db

from gameState.models import StateEnum

from .game_state_repository import GameStateRepository
from player.player_repository import PlayerRepository
from board.board_repository import BoardRepository
from movementCards.movement_cards_repository import MovementCardsRepository
from figureCards.figure_cards_repository import FigureCardsRepository

from player.player_logic import PlayerLogic, get_player_logic
from player.player_repository import PlayerRepository
from movementCards.movement_cards_logic import MovementCardLogic, get_mov_cards_logic
from figureCards.figure_cards_logic import FigureCardsLogic, get_fig_cards_logic

from board.board_logic import BoardLogic, get_board_logic
from partial_movement.partial_movement_logic import PartialMovementLogic, get_partial_movement_logic

from connection_manager import manager


game_state_router = APIRouter(
    prefix= "/game_state",
    tags=['GameStatus']
)

@game_state_router.get("/{game_id}/current_turn", status_code=status.HTTP_200_OK)
async def get_current_player(game_id: int, db: Session = Depends(get_db), 
                             game_state_repo: GameStateRepository = Depends()):    
    return game_state_repo.get_current_player(game_id, db)

@game_state_router.patch("/{game_id}/finish_turn", status_code= status.HTTP_200_OK)
async def finish_turn(game_id: int, game_state_repo:  GameStateRepository = Depends(), 
                        figure_card_repo:  FigureCardsRepository = Depends(), 
                        movement_card_repo: MovementCardsRepository = Depends(), 
                        partial_movement_logic: PartialMovementLogic = Depends(get_partial_movement_logic),
                        db: Session = Depends(get_db)
                    ):
    
    #Obtenemos el id del jugador que desea terminar su turno
    player_id = game_state_repo.get_current_player(game_id, db)
    
    #Nos deshacemos de los mov parciales
    movements_to_erase = partial_movement_logic.revert_partial_movements(game_id, player_id["current_player_id"],db)

    #Notificamos nuevo tablero
    # message = {
    #         "type": f"{game_id}:MOVEMENT_UPDATE"
    #     }
    # await manager.broadcast(message)
    
    #Cambiamos el turno actual
    next_player_id = game_state_repo.get_next_player_id(game_id, db)
    
    game_state_repo.update_current_player(game_id, next_player_id, db)
    
    #repartir cartas de movimiento y figuras si es necesario
    figure_card_repo.grab_figure_cards(player_id["current_player_id"], game_id, db)
    
    movement_card_repo.grab_mov_cards(player_id["current_player_id"], game_id, db)
    
    #notificar a los jugadores del nuevo turno
    message = {"type":f"{game_id}:NEXT_TURN"}
    await manager.broadcast(message)
    
    return {"message": "Current player successfully updated", "reverted_movements": movements_to_erase}


@game_state_router.patch("/start/{game_id}", status_code=status.HTTP_200_OK)
async def start_game(
    game_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    player_repo: PlayerRepository = Depends(),
    game_state_repo: GameStateRepository = Depends(),
    player_logic: PlayerLogic = Depends(get_player_logic),
    board_repo: BoardRepository = Depends(),
    mov_cards_logic: MovementCardLogic = Depends(get_mov_cards_logic),
    fig_cards_logic: FigureCardsLogic = Depends(get_fig_cards_logic),
    board_logic: BoardLogic = Depends(get_board_logic)
):
    # Step 1: Set up the game state so that it can be fetched immediately.
    players = player_repo.get_players_in_game(game_id, db)

    # Step 2: Assign random turns and set the current player
    first_player_id = player_logic.assign_random_turns(players, db)
    game_state_repo.update_game_state(game_id, StateEnum.PLAYING, db)
    game_state_repo.update_current_player(game_id, first_player_id, db)

    # Step 3: Create the board and decks for players
    board_creation_result = board_logic.configure_board(game_id, db)
    mov_deck_creation = mov_cards_logic.create_mov_deck(game_id, db)
    fig_deck_creation = fig_cards_logic.create_fig_deck(db, game_id)

    # Step 4: Notify players that the game has started
    message = {
        "type": f"GAMES_LIST_UPDATE"
    }


    await manager.broadcast(message)

    message = {
        "type": f"{game_id}:GAME_STARTED"
    }

    await manager.broadcast(message)

    return {"message": "Game status updated, you are playing!"}



@game_state_router.get("/{game_id}")
async def get_game_state(game_id: int, db: Session = Depends(get_db), repo: GameStateRepository = Depends()):
    return repo.get_game_state_by_id(game_id, db)
