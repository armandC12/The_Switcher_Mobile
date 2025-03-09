from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from movementCards.schemas import MovementCardSchema
from figureCards.schemas import FigureCardSchema

# schema del enum de turnos
class turnEnum(str,Enum):
    PRIMERO = "PRIMERO"
    SEGUNDO = "SEGUNDO"
    TERCERO = "TERCERO"
    CUARTO  = "CUARTO"


# schema de jugador
class PlayerInDB(BaseModel):
    id: int
    name: str
    turn: Optional[turnEnum] = None
    game_id: int
    game_state_id: int
    host: bool
    winner: bool
    
    model_config = ConfigDict(from_attributes = True)


class PlayerCreateMatch(BaseModel):
    name: str
    host: Optional[bool] = True
    turn: Optional[turnEnum] = None

class PlayerJoinRequest(BaseModel):
    player_name : str
    password: str | None = None