import random
from sqlalchemy.orm import Session
from .models import Board, Box, ColorEnum
from .schemas import BoardAndBoxesOut
from fastapi import HTTPException, status, Depends
from .board_repository import BoardRepository
from figureCards.figure_cards_repository import FigureCardsRepository
from player.player_repository import PlayerRepository
from figureCards.figure_cards_logic import get_fig_cards_logic

def get_board_logic(board_repo: BoardRepository = Depends()):
    return BoardLogic(board_repo)

class BoardLogic:
    
    def __init__(self, board_repo: BoardRepository):
        self.board_repo = board_repo
            
    def configure_board(self, game_id: int, db: Session):
        # Nos aseguramos que un tablero no haya sido creado
        existing_board = self.board_repo.get_existing_board(game_id, db)
        
        if existing_board:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board already exists")
        
        #Creamos un nuevo tablero
        new_board = self.board_repo.create_new_board(game_id, db)
        
        #Creamos una lista con los colores de las casillas
        colors = [ColorEnum.BLUE] * 9 + [ColorEnum.GREEN] * 9 + [ColorEnum.RED] * 9 + [ColorEnum.YELLOW] * 9
        random.shuffle(colors) # le damos un orden aleatorio
        
        #Creamos cada casilla y las guardamos en la DB
        for i, color in enumerate(colors):
                pos_x = i % 6
                pos_y = i // 6
                self.board_repo.add_box_to_board(new_board.id, game_id, color, pos_x, pos_y, db)
        
        return {"message": "Board created successfully"}

