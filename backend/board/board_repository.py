from fastapi import HTTPException, status
from sqlalchemy import null
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List

from game.models import Game
from gameState.models import StateEnum
from .models import Board, Box, ColorEnum

from figureCards.models import typeEnum

from .schemas import BoardOut, BoardAndBoxesOut, BoardPosition, BoxOut, Box as BoxDB


class BoardRepository:
    
    def get_existing_board(self, game_id: int, db: Session):
        board = db.query(Board).filter(Board.game_id == game_id).first()
        
        return BoardOut.model_validate(board) if board else None
    
    def create_new_board(self, game_id: int, db: Session):
        # Nos aseguramos que un tablero no haya sido creado TODO: Ver si es necesario
        # existing_board = self.get_existing_board(game_id, db)
        # if existing_board:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board already exists")
        
        # Chequeamos que el juego exista
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

        #Creamos un nuevo tablero
        new_board = Board(game_id=game_id)
        db.add(new_board)
        db.commit()
        db.refresh(new_board)

        # return new_board
        return BoardOut.model_validate(new_board) if new_board else None
        
        
    def add_box_to_board(self, board_id: int, game_id: int, color: ColorEnum, pos_x: int, pos_y: int, db: Session):
        new_box = Box(
            color=color,
            pos_x=pos_x,
            pos_y=pos_y,
            game_id=game_id,
            board_id=board_id,
            highlight = False
        )    
        db.add(new_box)
        db.commit()
        db.refresh(new_box)
        
        return new_box

    def get_configured_board(self, game_id: int, db: Session):
        """
        Get the board and its boxes of a given game

        Args:
            game_id (int): The id of the game

        Returns:
            dict: The board and its boxes in a list of lists
        """
        
        # chequear que el juego exista y este iniciado
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        if game.game_state.state != StateEnum.PLAYING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game not started")

        board = db.query(Board).filter(Board.game_id == game_id).first()

        if not board:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

        # Formato Lista de listas para las filas de las casillas
        rows_in_board : List[List[BoxOut]] = []
        for index in range(6):
            # Se queda con las casillas de la fila nro index
            boxes_row = db.query(Box).filter(Box.board_id == board.id, Box.pos_y == index).all()

            if not boxes_row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Boxes not found in row {index}")

            formatted_boxes_row = [
                {
                    "color": box.color,
                    "pos_x": box.pos_x,
                    "pos_y": box.pos_y,
                    "highlighted": box.highlight
                }
                for box in boxes_row
            ]

            rows_in_board.append(formatted_boxes_row)

        if not rows_in_board:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boxes rows not found")
        
        result = BoardAndBoxesOut(game_id=board.game_id, board_id=board.id, boxes=rows_in_board)
        
        return BoardAndBoxesOut.model_validate(result)

    def switch_boxes(self, game_id: int, pos_from: BoardPosition, pos_to: BoardPosition, db: Session):
        
        try:
            db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        
        try:
            box_from = db.query(Box).filter(Box.game_id == game_id,
                                            Box.pos_x == pos_from.pos[0],
                                            Box.pos_y == pos_from.pos[1]
                                           ).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Box not found")
        
        try:
            box_to = db.query(Box).filter(Box.game_id == game_id,
                                            Box.pos_x == pos_to.pos[0],
                                            Box.pos_y == pos_to.pos[1]
                                           ).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Box not found")
        
        # Intercambio colores
        box_to_new_color = box_from.color
        
        box_from.color = box_to.color
        box_to.color = box_to_new_color
        
        #Guardo los cambios
        db.commit()

        return {"message": "The board was succesfully updated"}

    def get_box_by_position(self, board_id: int, pos_x: int, pos_y: int, db: Session):
        # print box positions
        print(f"get_box_by_position: {pos_x}, {pos_y}")
        box = db.query(Box).filter(Box.board_id == board_id, Box.pos_x == pos_x, Box.pos_y == pos_y).first()
        if not box:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Box not found {pos_x}, {pos_y}")
        return BoxDB.model_validate(box) if box else None
    
    def highlight_box(self, box_id: int, db: Session):
        box = db.query(Box).filter(Box.id == box_id).first()
        if not box:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Box to highlight not found")

        box.highlight = True
        db.commit()
        
    def reset_highlight_for_all_boxes(self, game_id: int, db: Session):
        # Bulk update en todas las boxes
        result = db.query(Box).filter(Box.game_id == game_id).update({Box.highlight: False})
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No boxes found for the game")
        
        
        # Guardar cambios
        db.commit()
        
    def update_figure_id_box(self, box_id: int, figure_id: int, figure_type: typeEnum ,  db: Session):
        box = db.query(Box).filter(Box.id == box_id).first()
        if not box:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Box to highlight not found")

        box.figure_type = figure_type
        box.figure_id = figure_id
        db.commit()
        
    def reset_figure_for_all_boxes(self, game_id: int, db: Session):
        # Bulk update en todas las boxes
        result = db.query(Box).filter(Box.game_id == game_id).update({Box.figure_type: None, Box.figure_id: None})
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No boxes found for the game")
        
        # Guardar cambios
        db.commit()
        
    def get_figures(self, game_id: int, db: Session):
        # Query all boxes for the given game
        boxes = db.query(Box).filter(Box.game_id == game_id, Box.figure_id.is_not(None)).all()
        
        if not boxes:
            return []
        # Group boxes by figure_id
        figures = {}
        for box in boxes: 
            if box.figure_id not in figures:
                figures[box.figure_id] = []
            figures[box.figure_id].append({
                "color": box.color,
                "pos_x": box.pos_x,
                "pos_y": box.pos_y,
                "highlighted": box.highlight,
                "figure_id": box.figure_id,
                "figure_type": box.figure_type
            })
        
        # Convert the dictionary to a list of lists
        formatted_figures = [figures[figure_id] for figure_id in figures if figure_id is not None]
        
        return formatted_figures