import random
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from board.board_repository import BoardRepository
from board.models import Board, Box
from board.schemas import BoardAndBoxesOut, BoxOut, ColorEnum
from connection_manager import manager
from game.game_logic import get_game_logic
from game.game_repository import GameRepository
from game.schemas import GameInDB
from gameState.game_state_repository import GameStateRepository
from gameState.schemas import GameStateInDB 
from movementCards.movement_cards_repository import MovementCardsRepository
from partial_movement.partial_movement_repository import PartialMovementRepository
from player.player_repository import PlayerRepository

from .figure_cards_repository import FigureCardsRepository
from .schemas import PlayFigureCardInput, BlockFigureCardInput
from .models import (DirectionEnum, FigurePaths, direction_map, typeEnum)

from connection_manager import manager

SHOW_LIMIT = 3

class FigureCardsLogic:
    def __init__(
        self, 
        fig_card_repo: FigureCardsRepository, 
        player_repo: PlayerRepository,
        game_state_repo: GameStateRepository = None,
        game_repo: GameRepository = None,
        board_repo: BoardRepository = None,
        partial_mov_repo: PartialMovementRepository = None,
        mov_card_repo: MovementCardsRepository = None
    ) -> None:
        self.fig_card_repo = fig_card_repo
        self.player_repo = player_repo
        self.game_state_repo = game_state_repo
        self.game_repo = game_repo
        self.board_repo = board_repo
        self.partial_mov_repo = partial_mov_repo
        self.mov_card_repo = mov_card_repo
    
    def create_fig_deck(self, db: Session, game_id: int) -> dict:

        players = self.player_repo.get_players_in_game(game_id,db)

        if len(players) == 0:
            return {"message": "Figure deck was not created, there no players in game"}
        
        #Creamos una lista con los tipos de cartas de figuras
        
        hard_cards = [card for card in typeEnum if card.name.startswith('FIG') and not card.name.startswith('FIGE')]
        easy_cards = [card for card in typeEnum if card.name.startswith('FIGE')]

        hard_cards_per_player = 36 // len(players)
        easy_cards_per_player = 14 // len(players)
        
        for player in players:
            #Random
            random.shuffle(easy_cards)
            random.shuffle(hard_cards)

            player_cards = (hard_cards[:hard_cards_per_player] + easy_cards[:easy_cards_per_player])

            random.shuffle(player_cards)

            #armo el mazo para el jugador
            show = True
            for index, figure in enumerate(player_cards):
                if index == SHOW_LIMIT:
                    show = False
                self.fig_card_repo.create_figure_card(player.id, game_id, figure, show, False, db)

        return {"message": "Figure deck created"}

    def check_game_exists(self, game_id: int, db: Session) -> None:
        self.game_repo.get_game_by_id(game_id, db)
    

    def check_game_in_progress(self, game_id: int, db: Session) -> None:
        game = self.game_state_repo.get_game_state_by_id(game_id, db)
        
        if game is None:
            raise HTTPException(status_code=404, detail="Game not found when getting formed figures")
        if game.state != "PLAYING":
            raise HTTPException(status_code=404, detail="Game not in progress when getting formed figures")


    def get_board_or_404(self, game_id: int, db: Session) ->  BoardAndBoxesOut :
        board = self.board_repo.get_configured_board(game_id, db)
        if board is None:
            raise HTTPException(status_code=404, detail="Board not found when getting formed figures")
        return board


    def is_valid_pointer(self, pointer: tuple[int, int]) -> bool:
        return pointer[0] >= 0 and pointer[0] <= 5 and pointer[1] >= 0 and pointer[1] <= 5

    def check_surroundings(self, figure: list[BoxOut], pointer: tuple[int,int], board: BoardAndBoxesOut, color: ColorEnum, db: Session) -> bool:
        if color != board.boxes[pointer[1]][pointer[0]].color:
            return False
        # chequear que las casillas de alrededor del pointer dado sean de distinto color
        for direction in DirectionEnum:
            # chequear que la casilla de alrededor de la figura sea del color de la figura
            pointerBefore = pointer
            pointer = self.move_pointer(pointer, direction)
            if self.is_valid_pointer(pointer):
                box = board.boxes[pointer[1]][pointer[0]]
                box_color = box.color
                bel_to_fig = self.belongs_to_figure(pointer, figure)
                if (box_color == color) and not bel_to_fig:
                    return False
                
            # retrotraer el pointer    
            pointer = pointerBefore
                
        return True


    def move_pointer(self, pointer: tuple[int,int], direction: DirectionEnum) -> tuple[int,int]:
        if direction == DirectionEnum.UP:
            pointer = (pointer[0], pointer[1] - 1)
        elif direction == DirectionEnum.DOWN:
            pointer = (pointer[0], pointer[1] + 1)
        elif direction == DirectionEnum.LEFT:
            pointer = (pointer[0] - 1, pointer[1])
        elif direction == DirectionEnum.RIGHT:
            pointer = (pointer[0] + 1, pointer[1])
        return pointer


    def belongs_to_figure(self, pointer: tuple[int,int], figure: list[BoxOut]) -> bool:
        for fig_box in figure:
            if fig_box.pos_x == pointer[0] and fig_box.pos_y == pointer[1]:
                return True
        return False


    def check_path_blind(self, path: list[DirectionEnum], pointer: tuple[int, int], board: BoardAndBoxesOut, color: ColorEnum, figure_id: int, figure_type: str, db: Session, board_figure: Optional[list[BoxOut]] = None) -> Union[bool, list[BoxOut]]:
        result = True
        figure = [] # list of boxes that form the figure

        if board_figure is not None:
            # check if the current pointer points to a box from our figure
            inBounds = self.belongs_to_figure(pointer, board_figure)
            if not inBounds:
                raise HTTPException(status_code=404, detail="Boxes given out of type figure bounds")

        # Agregamos la casilla inicial a la figura formada
        first_box = board.boxes[pointer[1]][pointer[0]]
        figure.append(first_box)
        
        for direction in path:
            pointer = self.move_pointer(pointer, direction)

            if not self.is_valid_pointer(pointer):
                result = False
                break
            box = board.boxes[pointer[1]][pointer[0]]
            if box.color != color:
                result = False
                break
            if board_figure is not None:
                # check if the current pointer points to a box from our figure
                if not self.belongs_to_figure(pointer, board_figure):
                    result = False
                    break
            # Agregar la casilla a la figura formada
            figure.append(box)

        # si obtuvimos una figura valida, chequear que no sea contigua a ningun otro color de su mismo tipo
        if result:
            for fig_box in figure:
                if not self.check_surroundings(figure, (fig_box.pos_x, fig_box.pos_y), board, color, db):
                    return False
            
            if (figure_type is not None) and (figure_id is not None):
                for fig_box in figure:
                    # highlight the box in the board
                    fig_box = self.board_repo.get_box_by_position(board.board_id, fig_box.pos_x, fig_box.pos_y, db)
                    self.board_repo.highlight_box(fig_box.id, db)
                    self.board_repo.update_figure_id_box(fig_box.id, figure_id, figure_type, db)
                    fig_box.highlighted = True
              
            return figure # return the figure if it is valid

        return result


    def get_pointer_from_figure(self, figure: list[BoxOut], rot: int) -> tuple[int,int]:
        if len(figure) == 0:
            raise HTTPException(status_code=404, detail="Empty figure")

        x = figure[0].pos_x
        y = figure[0].pos_y
        # dependiendo de la rotacion aplicada actualmente, el punto de referencia de la figura
        # (0 grados = punta arriba izquierda) (90g = punta arriba derecha) (180 = punta abajo derecha) (270 = punta abajo izquierda)
        # los elementos 0,0 estan en la punta izquierda mas alta

        if rot == 0:
            min_x = min(box.pos_x for box in figure)
            min_x_boxes = [box for box in figure if box.pos_x == min_x]
            min_y = min(box.pos_y for box in min_x_boxes)
            x = min_x
            y = min_y
        elif rot == 1:
            max_y = max(box.pos_y for box in figure)
            max_y_boxes = [box for box in figure if box.pos_y == max_y]
            min_x = min(box.pos_x for box in max_y_boxes)
            x = min_x
            y = max_y
        elif rot == 2:
            max_x = max(box.pos_x for box in figure)
            max_x_boxes = [box for box in figure if box.pos_x == max_x]
            max_y = max(box.pos_y for box in max_x_boxes)
            x = max_x
            y = max_y
        elif rot == 3:
            min_y = min(box.pos_y for box in figure)
            min_y_boxes = [box for box in figure if box.pos_y == min_y]
            max_x = max(box.pos_x for box in min_y_boxes)
            x = max_x
            y = min_y
        else:
            raise HTTPException(status_code=404, detail="Invalid rotation")

        return (x,y)


    def check_valid_figure(self, figure: list[BoxOut], figure_type: str, board: BoardAndBoxesOut, db: Session) -> bool:
        pointer = self.get_pointer_from_figure(figure,0)
        color = board.boxes[pointer[1]][pointer[0]].color
        if color != figure[0].color:
            raise HTTPException(status_code=404, detail="Color of figure does not match with color in board")
        validType = False
        partial_result = False
        result = False
        for path in FigurePaths:
            if path.type == figure_type:
                for _ in range(4):
                    for rot in range(4):
                        pointer = self.get_pointer_from_figure(figure, rot)
                        partial_result = self.check_path_blind(path.path, pointer, board, color, None, None, db, figure)
                        if partial_result:
                            result = True
                            break

                    # Rota el path 90 grados
                    path.path = [direction_map[direction] for direction in path.path]
                    if partial_result:
                        break

                validType = True
                break
        if partial_result == {'message': "Boxes given out of type figure bounds"}:
            raise HTTPException(status_code=404, detail="Boxes given out of type figure bounds")

        if not validType:
            raise HTTPException(status_code=404, detail="Invalid figure type")

        return result


    async def play_figure_card(self, figureInfo: PlayFigureCardInput, db: Session) -> dict:
        # chequear que el juego exista y este en progreso
        self.check_game_exists(figureInfo.game_id, db)
        self.check_game_in_progress(figureInfo.game_id, db)
        player = self.player_repo.get_player_by_id(figureInfo.game_id, figureInfo.player_id, db)
        gameState = self.game_state_repo.get_game_state_by_id(figureInfo.game_id, db)

        #chequear que no se este adquiriendo una figura del color prohibido
        if gameState.forbidden_color is not None:
            if gameState.forbidden_color.name == figureInfo.figure[0].color:
                return {"message": "No se puede adquirir una figura del color prohibido"}

        # chequear que sea el turno del jugador
        if player.id != gameState.current_player:
            return {"message": "It is not the player's turn"}

        board = self.board_repo.get_configured_board(figureInfo.game_id, db)
        figure_card = self.fig_card_repo.get_figure_card_by_id(figureInfo.game_id, figureInfo.player_id, figureInfo.card_id, db)

        # chequear que la carta de figura sea del jugador
        if figure_card.player_id != player.id:
            return {"message": "The figure card does not belong to the player"}
        if not figure_card.show:
            return {"message": "The card is not shown"}
        if figure_card.blocked:
            return {"message": "CARD BLOCKED!!!"}
        
        # chequear que la figura es valida (compara con la figura de la carta)
        valid = self.check_valid_figure( figureInfo.figure, figure_card.type, board, db)

        if valid:
            # Eliminar carta de figura
            self.fig_card_repo.discard_figure_card(figureInfo.card_id, db)
            
            self.partial_mov_repo.delete_all_partial_movements_by_player(figureInfo.player_id, db)
            self.mov_card_repo.discard_all_player_partially_used_cards(figureInfo.player_id, db)

            # Actualizar color prohibido
            self.game_state_repo.update_forbidden_color(figureInfo.game_id, figureInfo.figure[0].color, db)

            # Avisar por websocket que se jugo una carta de figura
            game_id = figureInfo.game_id

            game_logic = get_game_logic(self.game_repo , self.game_state_repo, self.player_repo, self.fig_card_repo)
            if game_logic.check_win_condition_no_figure_cards(figureInfo.game_id, figureInfo.player_id, db):
                await game_logic.handle_win(game_id, figureInfo.player_id, db)

            message = {
                    "type":f"{game_id}:FIGURE_UPDATE"
                }
            await manager.broadcast(message)

            return {"message": "Figure card played"}
        else:
            return {"message": "Invalid figure"}

    # Logica de resaltar figuras formadas
    
    def has_minimum_length(self, pointer: tuple[int,int], board: BoardAndBoxesOut, color: ColorEnum, db: Session, min_length: int) -> bool:
        length = 0
        queue = [pointer]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            box = board.boxes[current[1]][current[0]]
            if box.color == color:
                length += 1
                if length >= min_length:
                    return True
                for direction in DirectionEnum:
                    next_pointer = self.move_pointer(current, direction)
                    if self.is_valid_pointer(next_pointer) and next_pointer not in visited:
                        queue.append(next_pointer)
        return False


    def is_pointer_different_from_formed_figures(self, pointer: tuple[int,int], figures: list[list[BoxOut]]) -> Union[bool, tuple[int,int]]:
        for figure in figures:
            for fig_box in figure:
                if fig_box.pos_x == pointer[0] and fig_box.pos_y == pointer[1]:
                    return False
        return pointer
    

    async def get_formed_figures(self, game_id: int, db: Session) -> None:
        # Chequear que el juego exista y este en progreso
        self.check_game_exists(game_id, db)
        self.check_game_in_progress(game_id, db)

        board = self.get_board_or_404(game_id, db)

        # Reset del tablero
        self.board_repo.reset_highlight_for_all_boxes(game_id, db)
        self.board_repo.reset_figure_for_all_boxes(game_id, db)
        
        figures = []
        figure_or_bool = False
        figure_id = 0
        
        possible_paths = self.fig_card_repo.fetch_shown_figure_card_types(game_id, db)
        filtered_figure_paths = [fp for fp in FigurePaths if fp.type in possible_paths]

        for i, row in enumerate(board.boxes):
            for j, box in enumerate(row):
                # Asignar pointer siempre y cuando sea distinto de las posiciones de las figuras ya formadas
                pointer = self.is_pointer_different_from_formed_figures((j,i), figures)
                print(f"\n(get_formed_figures) pointer new or false : {pointer}\n")
                if pointer is False:
                    continue
                color = box.color

                # Check if there are at least 4 adjacent blocks of the same color before applying paths
                if not self.has_minimum_length(pointer, board, color, db, min_length=4):
                    continue
                
                for path in filtered_figure_paths:
                    for _ in range(4): # 4 rotaciones del path
                        figure_or_bool = self.check_path_blind(path.path, pointer, board, color,figure_id, path.type, db)
                        if figure_or_bool is not False :
                            figures.append(figure_or_bool)
                            figure_id += 1
                            break
                        path.path = [direction_map[direction] for direction in path.path]
                    
                    if figure_or_bool is not False:
                        break

    
    def check_valid_block(self, figureInfo: BlockFigureCardInput, db) -> bool:
        figure_card = self.fig_card_repo.get_figure_card_by_id(figureInfo.game_id, figureInfo.blocked_player_id, figureInfo.card_id, db)
        if not figure_card.show:
            return False

        figure_cards = self.fig_card_repo.get_figure_cards(figureInfo.game_id, figureInfo.blocked_player_id, db)

        has_blocked = any(card.blocked and card.show for card in figure_cards)
        
        if has_blocked:
            return False
        
        show_figure_cards = sum(1 for card in figure_cards if card.show)
        if show_figure_cards == 1:
            return False

        board = BoardRepository.get_configured_board(self.board_repo, figureInfo.game_id, db)

        if not self.check_valid_figure( figureInfo.figure, figure_card.type, board, db):
            return False

        gameState = self.game_state_repo.get_game_state_by_id(figureInfo.game_id, db)

        #chequear que no se este bloqueando una figura del color prohibido
        if gameState.forbidden_color is not None:
            if gameState.forbidden_color.name == figureInfo.figure[0].color:
                return False

        return True
    

    async def block_figure_card(self, figureInfo: BlockFigureCardInput, db):
        valid = self.check_valid_block(figureInfo, db)

        if valid:
            self.partial_mov_repo.delete_all_partial_movements_by_player(figureInfo.blocker_player_id, db)
            self.mov_card_repo.discard_all_player_partially_used_cards(figureInfo.blocker_player_id, db)
            self.game_state_repo.update_forbidden_color(figureInfo.game_id, figureInfo.figure[0].color, db)

            message = {
                
                "type": f"{figureInfo.game_id}:BOARD_UPDATE",
            }
            
            await manager.broadcast(message)

            message = {
                "type": f"{figureInfo.game_id}:BLOCK_CARD",
            }

            await manager.broadcast(message)

            return self.fig_card_repo.block_figure_card(figureInfo.game_id, figureInfo.card_id, db)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid blocking")
                    
    def check_need_to_unblock_card(self, game_id,  player_id, db: Session) -> bool:
        unblock = False
        cards_left = self.fig_card_repo.get_figure_cards(game_id, player_id, db)
        
        cards_in_hand = [card for card in cards_left if card.show]

        if len(cards_in_hand) == 1 and cards_in_hand[0].blocked:
            unblock = True
            self.fig_card_repo.unblock_figure_card(cards_in_hand[0].id, db)
            self.fig_card_repo.soft_block_figure_card(cards_in_hand[0].id, db)

        return unblock
                    

def get_fig_cards_logic(fig_card_repo: FigureCardsRepository = Depends(), 
                        player_repo: PlayerRepository = Depends(),
                        game_state_repo: GameStateRepository = Depends(),
                        game_repo: GameRepository = Depends(),
                        board_repo: BoardRepository = Depends(),
                        partial_mov_repo: PartialMovementRepository = Depends(),
                        mov_card_repo: MovementCardsRepository = Depends()
                        ):
    return FigureCardsLogic(fig_card_repo, player_repo, game_state_repo, game_repo, board_repo, partial_mov_repo, mov_card_repo)
