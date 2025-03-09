from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict
from game.models import Game
from gameState.models import GameState, StateEnum
from board.models import ColorEnum

# Schema del estado de la partida  
class GameStateInDB(BaseModel):
    id           : int
    state        : StateEnum
    game_id       : int
    current_player: Optional[int]
    forbidden_color: Optional[ColorEnum] = None
    #mazo movimiento falta

    model_config = ConfigDict(from_attributes = True)

class GameStateCreate(BaseModel):
    state        : StateEnum
    current_player: Optional[int]
    #mazo movimiento falta
    