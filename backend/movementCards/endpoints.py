from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db

from .movement_cards_repository import MovementCardsRepository, get_movement_cards_repository
from .movement_cards_logic import MovementCardLogic, get_mov_cards_logic
from .schemas import PlayMovementCardRequest

from board.schemas import BoardPosition
from board.board_repository import BoardRepository
from partial_movement.partial_movement_repository import PartialMovementRepository, get_partial_movement_repository

from figureCards.figure_cards_logic import FigureCardsLogic, get_fig_cards_logic
from connection_manager import manager

movement_cards_router = APIRouter(
    prefix= "/deck/movement",
    tags=['MovementCards']
)

@movement_cards_router.get("/{game_id}")
async def get_players_movement_cards(game_id: int, 
                                     db: Session = Depends(get_db), 
                                     repo: MovementCardsRepository = Depends(get_movement_cards_repository)
                                    ):
    
    return repo.get_players_movement_cards(game_id, db)


# Obtener cartas de movimiento
@movement_cards_router.get("/{game_id}/{player_id}")
async def get_movement_cards(game_id: int, player_id: int, 
                             db: Session = Depends(get_db), 
                             repo: MovementCardsRepository = Depends(get_movement_cards_repository)):
    
    return repo.get_movement_cards(game_id, player_id, db)

# Obtener todas las cartas de movimiento
@movement_cards_router.get("/{game_id}/{player_id}/{card_id}")
async def get_movement_card_by_id(game_id: int, player_id: int, 
                                  card_id: int, db: Session = Depends(get_db), 
                                  repo: MovementCardsRepository = Depends(get_movement_cards_repository)):
    
    return repo.get_movement_card_by_id(game_id, player_id, card_id, db)

@movement_cards_router.post("/play_card", status_code = status.HTTP_201_CREATED)
async def play_movement_card(
                                request: PlayMovementCardRequest,
                                mov_cards_logic: MovementCardLogic = Depends(get_mov_cards_logic), 
                                partial_mov_repo: PartialMovementRepository = Depends() ,
                                mov_cards_repo: MovementCardsRepository = Depends(),
                                board_repo: BoardRepository = Depends(),
                                fig_logic: FigureCardsLogic = Depends(get_fig_cards_logic),
                                db: Session = Depends(get_db)
                            ):
    #validar movimiento
    movement_validate = mov_cards_logic.validate_movement(request.card_id, request.pos_from, request.pos_to, db)
    #si el movimiento no es valido se le debe avisar el problema al jugador (?) 
    if not movement_validate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movement")
    
    
    #si el movimiento es valido entonces lo registramos como un movimiento parcial
    partial_mov_repo.create_partial_movement(request.game_id, request.player_id, request.card_id, request.pos_from, request.pos_to, db)
    
    #registar carta de movimiento como parcialmente usada
    mov_cards_repo.mark_card_partially_used(request.card_id,db)
    
    #se realizan los cambios en el tablero
    board_repo.switch_boxes(request.game_id, request.pos_from, request.pos_to, db) 
    #se avisa a los jugadores del nuevo tablero
    message = {
            "type": f"{request.game_id}:MOVEMENT_UPDATE"
        }
    await manager.broadcast(message)
    
    #Cambiar mensaje
    return {"message": "Great move..."}


@movement_cards_router.post("/{game_id}/{player_id}/undo_move")
async def undo_movement(game_id: int, player_id: int, db: Session = Depends(get_db), 
                        partial_mov_repo:  PartialMovementRepository = Depends(get_partial_movement_repository),
                        board_repo: BoardRepository = Depends(),
                        mov_cards_repo: MovementCardsRepository = Depends(get_movement_cards_repository)
                        ):

    last_movement = partial_mov_repo.undo_movement(game_id,player_id,db)
    pos_from = BoardPosition(pos=(last_movement.pos_from_x, last_movement.pos_from_y))
    pos_to = BoardPosition(pos=(last_movement.pos_to_x, last_movement.pos_to_y))

    board_repo.switch_boxes(game_id, pos_from, pos_to, db)
    
    mov_cards_repo.mark_card_in_player_hand(last_movement.mov_card_id, db)
    
    movement_update = {
            "type": f"{game_id}:MOVEMENT_UPDATE"
    }
    
    await manager.broadcast(movement_update)

    return {"message": "The movement was undone successfully"}
    
