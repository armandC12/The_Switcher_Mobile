from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, ConfigDict
from .models import typeEnum, DifficultyEnum
from board.schemas import BoxIn, BoxOut

# Schema de cartas de figura
class FigureCardSchema(BaseModel):
    id: int
    type: typeEnum
    show: bool
    difficulty: Optional[DifficultyEnum] = None
    player_id: int
    game_id :  int
    blocked: bool
    soft_blocked: bool
    
    
    model_config = ConfigDict(from_attributes = True)
    
    
class PlayFigureCardInput(BaseModel):
    player_id: int
    game_id: int
    card_id: int
    figure: List[BoxIn]


class BlockFigureCardInput(BaseModel):
    blocked_player_id: int
    blocker_player_id: int
    game_id: int
    card_id: int
    figure: List[BoxOut]