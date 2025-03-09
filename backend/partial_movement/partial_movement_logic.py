from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from sqlalchemy.exc import NoResultFound

from .models import PartialMovements
from .partial_movement_repository import PartialMovementRepository
from board.schemas import BoardPosition
from board.board_repository import BoardRepository

from movementCards.movement_cards_repository import MovementCardsRepository

def get_partial_movement_logic(board_repo: BoardRepository = Depends(), partial_repo: PartialMovementRepository = Depends(), mov_card_repo : MovementCardsRepository = Depends()):
    return PartialMovementLogic(board_repo,partial_repo , mov_card_repo)

class PartialMovementLogic:
    def __init__(self, board_repo: BoardRepository, 
                       partial_repo: PartialMovementRepository,
                       mov_card_repo : MovementCardsRepository):
        self.board_repo = board_repo
        self.partial_repo = partial_repo
        self.mov_card_repo = mov_card_repo
        
    def revert_partial_movements(self, game_id: int, 
                                 player_id: int, 
                                 db: Session
                                ):
        # Obtener todos los movimientos parciales asociados con el jugador
        partial_movements = self.partial_repo.return_partial_movements_by_player(game_id,player_id,db)
        
        if not partial_movements:
            return False
        
        for movement in partial_movements:
            # Usamos switch boxes para revertir los cambios en el tablero
            pos_from = BoardPosition(pos=[movement.pos_from_x, movement.pos_from_y])
            pos_to = BoardPosition(pos=[movement.pos_to_x, movement.pos_to_y])
            self.board_repo.switch_boxes(game_id, pos_to, pos_from, db)

            # Volvemos a marcar la carta como no usada
            self.mov_card_repo.mark_card_in_player_hand(movement.mov_card_id,db)
            # Eliminamos el movimiento
            self.partial_repo.undo_movement_by_id(movement.id, db)
            
        return True