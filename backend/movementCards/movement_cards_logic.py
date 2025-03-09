import random
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .schemas import typeEnum
from .movement_cards_repository import MovementCardsRepository
from .utils import MovementCardUtils

from board.schemas import BoardPosition

from player.player_repository import PlayerRepository

from database.db import get_db

class MovementCardLogic:
    
    def __init__(
        self, mov_card_repo: MovementCardsRepository, player_repo: PlayerRepository, utils: MovementCardUtils
    ):
        self.mov_card_repo = mov_card_repo
        self.player_repo = player_repo
        self.utils = utils
        
    def create_mov_deck(self, game_id: int, db: Session):
        
        #Creamos una lista con los tipos de cartas de movimiento
        types_list = ([typeEnum.DIAGONAL_CONT] * 6 +
                        [typeEnum.DIAGONAL_ESP] * 6  + 
                        [typeEnum.EN_L_DER] * 6 + 
                        [typeEnum.EN_L_IZQ] * 6 + 
                        [typeEnum.LINEAL_AL_LAT] * 5 +
                        [typeEnum.LINEAL_CONT] * 5 +
                        [typeEnum.LINEAL_ESP] * 6
                        )  
        #Random
        random.shuffle(types_list)
        
        #
        for index,type in enumerate(types_list):
            self.mov_card_repo.create_movement_card(game_id, type, index, db)
        
        # asigno 3 a cada jugador
        players = self.player_repo.get_players_in_game(game_id,db)

        if len(players) == 0:
            return {"message": "Movement deck was not created because there are no players in game"}

        for player in players:
            # obtengo las cartas del juego que quedan en el deck (las que no fueron asignadas a un player aun)
            movDeck = self.mov_card_repo.get_movement_deck(game_id, db)

            # tomo 3 random
            asigned_mov_cards = random.sample(movDeck, 3)

            # las asigno
            for asigned_mov_card in asigned_mov_cards:
                self.mov_card_repo.assign_mov_card(asigned_mov_card.id, player.id, db);


        return {"message": "Movement deck created and assigned to players"}
    
    def validate_movement(self, card_id: int , pos_from: BoardPosition , pos_to: BoardPosition, db: Session):
        
        if not isinstance(pos_from, BoardPosition) or not isinstance(pos_to, BoardPosition):
            raise TypeError("pos_from and pos_to must be instances of BoardPosition")
        
        #ver tipo de figura
        movement_type = self.mov_card_repo.get_movement_card_type(card_id, db)
        
        #una funcion de validar por cada caso
        validation_functions = {
            typeEnum.LINEAL_CONT: self.validate_lineal_cont,
            typeEnum.LINEAL_ESP: self.validate_lineal_esp,
            typeEnum.DIAGONAL_CONT: self.validate_diagonal_cont,
            typeEnum.DIAGONAL_ESP: self.validate_diagonal_esp,
            typeEnum.EN_L_DER: self.validate_en_l_der,
            typeEnum.EN_L_IZQ: self.validate_en_l_izq,
            typeEnum.LINEAL_AL_LAT: self.validate_lineal_al_lat,
        }
        validate_function = validation_functions.get(movement_type)

        if not validate_function:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movement type")
        
        return validate_function(pos_from, pos_to)
    
    def validate_lineal_cont(self, pos_from: BoardPosition, pos_to: BoardPosition) -> bool:
        # Lógica de validación para LINEAL_CONT
        x_diff, y_diff = self.utils.calculate_differences(pos_from, pos_to)

        is_vertical = x_diff == 0 and y_diff == 1
        is_horizontal = y_diff == 0 and x_diff == 1
        
        return is_vertical or is_horizontal

    def validate_lineal_esp(self, pos_from: BoardPosition, pos_to: BoardPosition) -> bool:
        # Lógica de validación para LINEAL_ESP
        #Diferencia absoluta entre las posiciones x e y de las casillas
        x_diff, y_diff = self.utils.calculate_differences(pos_from, pos_to)

        is_vertical = x_diff == 0 and y_diff == 2
        is_horizontal = y_diff == 0 and x_diff == 2
        
        return is_vertical or is_horizontal

    def validate_diagonal_cont(self, pos_from: BoardPosition, pos_to: BoardPosition) -> bool:
        # Lógica de validación para DIAGONAL_CONT
        
        #Diferencia absoluta entre las posiciones x e y de las casillas
        x_diff, y_diff = self.utils.calculate_differences(pos_from, pos_to)

        #Chequeamos que la diferencia sea de exactamente 1 (para hacer la diagonal contigua)
        return x_diff == 1 and y_diff == 1

    def validate_diagonal_esp(self, pos_from: BoardPosition, pos_to: BoardPosition) -> bool:
        # Lógica de validación para DIAGONAL_ESP
        
        #Diferencia absoluta entre las posiciones x e y de las casillas
        x_diff, y_diff = self.utils.calculate_differences(pos_from, pos_to)

        #Chequeamos que la diferencia sea de exactamente 2 (para hacer la diagonal con un espacio)
        return x_diff == 2 and y_diff == 2

    def validate_en_l_izq(self, pos_from: BoardPosition, pos_to: BoardPosition) -> bool:
        # Lógica de validación para EN_L_IZQ
        x1, y1 = pos_from.pos[0], pos_from.pos[1]
        x2, y2 = pos_to.pos[0], pos_to.pos[1]
        
        x_diff, y_diff = self.utils.calculate_differences(pos_from, pos_to)
        
        #Dos movimientos en x, uno en y 
        if x_diff == 2 and y_diff == 1:
            # Verifico L hacia la izquierda
            if ( x2 > x1 and y2 > y1) or (x2 < x1 and y2 < y1):
                return True

        # Dos movimientos en y, uno en x
        if y_diff == 2 and x_diff == 1:
            # Verifico L hacia la izquierda
            if (y2 > y1 and x2 < x1) or (y2 < y1 and x2 > x1):
                return True

        return False

    def validate_en_l_der(self, pos_from: BoardPosition, pos_to: BoardPosition) -> bool:
        # Lógica de validación para EN_L_DER
        x1, y1 = pos_from.pos[0], pos_from.pos[1]
        x2, y2 = pos_to.pos[0], pos_to.pos[1]
        
        x_diff, y_diff = self.utils.calculate_differences(pos_from, pos_to)
        
        #Dos movimientos en x, uno en y 
        if x_diff == 2 and y_diff == 1:
            # Verifico L hacia la derecha
            if ( x2 > x1 and y2 < y1) or (x2 < x1 and y2 > y1):
                return True

        # Dos movimientos en y, uno en x
        if y_diff == 2 and x_diff == 1:
            # Verifico L hacia la derecha
            if (y2 < y1 and x2 < x1) or (y2 > y1 and x2 > x1):
                return True

        return False

        
    def validate_lineal_al_lat(self, pos_from: BoardPosition, pos_to: BoardPosition) -> bool:
        # Lógica de validación para LINEAL_AL_LAT
        # Obtener las coordenadas de la posición inicial y final
        from_x, from_y = pos_from.pos
        to_x, to_y = pos_to.pos
        
        # Verificar si la posición final está en uno de los extremos de la misma fila o columna
        is_same_column = from_x == to_x and ((to_y == 0 or to_y == 5) or  (from_y == 0 or from_y == 5))
        is_same_row = from_y == to_y and ((to_x == 0 or to_x == 5) or (from_x == 0 or from_x == 5))
        
        return is_same_row or is_same_column
    

def get_mov_cards_logic(mov_card_repo: MovementCardsRepository = Depends(), player_repo: PlayerRepository = Depends(), utils: MovementCardUtils = Depends()):
    return MovementCardLogic(mov_card_repo, player_repo, utils)
    