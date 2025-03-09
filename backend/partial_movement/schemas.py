from pydantic import BaseModel, Field
from typing import Optional

class PartialMovementsBase(BaseModel):
    pos_from_x: int = Field(..., ge=0, le=5)
    pos_from_y: int = Field(..., ge=0, le=5)
    pos_to_x: int = Field(..., ge=0, le=5)
    pos_to_y: int = Field(..., ge=0, le=5)
    game_id: int
    player_id: int
    mov_card_id: int

