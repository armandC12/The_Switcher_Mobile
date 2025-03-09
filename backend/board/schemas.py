from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Tuple, Annotated, Optional
from figureCards.models import typeEnum
class ColorEnum(str, Enum):
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"

    
class Box(BaseModel):
    id: int
    color: ColorEnum
    pos_x: int
    pos_y: int
    highlighted: bool = False
    
    model_config = ConfigDict(from_attributes = True)



class BoxOut(BaseModel):
    color: ColorEnum
    pos_x: int
    pos_y: int
    highlighted: bool = False
    figure_id: Optional[int] = None
    figure_type: Optional[typeEnum] = None

    model_config = ConfigDict(from_attributes = True)

class BoxIn(BaseModel):
    color: ColorEnum
    pos_x: int
    pos_y: int

    model_config = ConfigDict(from_attributes = True)
    
class BoardOut(BaseModel):
    game_id: int
    id: int

    model_config = ConfigDict(from_attributes = True)

class BoardAndBoxesOut(BaseModel):
    game_id: int
    board_id: int
    boxes: List[List[BoxOut]]
    formed_figures: List[List[BoxOut]] = []

    model_config = ConfigDict(from_attributes = True)

class BoardPosition(BaseModel):
    pos: Tuple[Annotated[int, Field(ge=0, le=5)], Annotated[int, Field(ge=0, le=5)]]
    class ConfigDict:
        # Allows validation at the time of initialization
        validate_assignment = True