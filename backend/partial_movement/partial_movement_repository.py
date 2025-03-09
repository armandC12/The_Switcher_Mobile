from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from sqlalchemy import select

from .models import PartialMovements

from board.schemas import BoardPosition
from game.models import Game
from player.models import Player
from movementCards.models import MovementCard


class PartialMovementRepository:
  
    def create_partial_movement(self, game_id: int, player_id: int, card_id: int, pos_from: BoardPosition , pos_to: BoardPosition, db: Session):
        # Verificamos exist el juego
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        
        # verificamos si existe el jugador en el juego
        player = db.query(Player).filter(Player.id == player_id, Player.game_id == game_id).first()
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found in the specified game")
        
        # cerificamos si existe la carta en la mano del jugador en el juego
        card = db.query(MovementCard).filter(MovementCard.id == card_id, 
                                             MovementCard.player_id == player_id, 
                                             MovementCard.game_id == game_id
                                            ).first()
        if not card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found for the specified player and game")
        
        partial_movement = PartialMovements(
            game_id=game_id,
            player_id=player_id,
            mov_card_id=card_id,
            pos_from_x=pos_from.pos[0],
            pos_from_y=pos_from.pos[1],
            pos_to_x=pos_to.pos[0],
            pos_to_y=pos_to.pos[1]
        )
        
        db.add(partial_movement)
        db.commit()

    # se comporta como un pop de un stack    
    def undo_movement(self, game_id: int, player_id: int, db: Session) -> PartialMovements:
        # busco la ultima fila de la tabla partial movements para el juego y jugador especificados
        last_parcial_movement = db.execute(
            select(PartialMovements)
            .filter_by(game_id=game_id, player_id=player_id)
            .order_by(PartialMovements.id.desc())
        ).scalar()
        
        if last_parcial_movement is None:
            raise HTTPException(status_code=404, detail="There is no partial movement to undo")

        # elimino la fila
        db.delete(last_parcial_movement)

        db.commit()

        # devuelvo el movimiento eliminado
        return last_parcial_movement
    
    def return_partial_movements_by_player(self, game_id: int, player_id: int, db: Session):
        # Obtener todos los movimientos parciales asociados con el jugador
        partial_movements = db.query(PartialMovements).filter(
            PartialMovements.game_id == game_id,
            PartialMovements.player_id == player_id
        ).all()

        if not partial_movements:
            return []
        
        return partial_movements
    
    def undo_movement_by_id(self, movement_id, db: Session):
        partial_movement = db.query(PartialMovements).filter(PartialMovements.id == movement_id).first()
        
        if not partial_movement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partial movement not found")
        
        db.delete(partial_movement)
        db.commit()

    def delete_all_partial_movements_by_player(self,player_id: int, db: Session):
        
        db.query(PartialMovements).filter(
            PartialMovements.player_id == player_id
        ).delete(synchronize_session=False)
        
        db.commit()


def get_partial_movement_repository(partial_movement_repo: PartialMovementRepository = Depends()) -> PartialMovementRepository:
    return partial_movement_repo
