from enum import Enum
from typing import List
from sqlalchemy import Column, Integer, Boolean, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# Definir un enum de dificultades
class DifficultyEnum(str,Enum):
    EASY = "EASY"
    HARD = "HARD"

class typeEnum(str, Enum):
    FIG01 = "FIG01"
    FIG02 = "FIG02"
    FIG03 = "FIG03"
    FIG04 = "FIG04"
    FIG05 = "FIG05"
    FIG06 = "FIG06"
    FIG07 = "FIG07"
    FIG08 = "FIG08"
    FIG09 = "FIG09"
    FIG10 = "FIG10"
    FIG11 = "FIG11"
    FIG12 = "FIG12"
    FIG13 = "FIG13"
    FIG14 = "FIG14"
    FIG15 = "FIG15"
    FIG16 = "FIG16"
    FIG17 = "FIG17"
    FIG18 = "FIG18"
    FIGE01 = "FIGE01"
    FIGE02 = "FIGE02"
    FIGE03 = "FIGE03"
    FIGE04 = "FIGE04"
    FIGE05 = "FIGE05"
    FIGE06 = "FIGE06"
    FIGE07 = "FIGE07"

# Modelo de carta de figura
class FigureCard(Base):
    __tablename__ = 'figure_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    show = Column(Boolean, nullable=False)
    difficulty = Column(SQLAEnum(DifficultyEnum), nullable=True)
    player_id = Column(Integer, ForeignKey('players.id', use_alter=True, ondelete='CASCADE'), nullable=False)
    type = Column(SQLAEnum(typeEnum), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    blocked = Column(Boolean, nullable=False)
    soft_blocked = Column(Boolean, nullable=False)
    
    player = relationship("Player", back_populates="figure_cards")
    game = relationship("Game", back_populates="figure_cards")


class DirectionEnum(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

# Mapeo de cada dirección a la siguiente
direction_map = {
    "UP": "RIGHT",
    "RIGHT": "DOWN",
    "DOWN": "LEFT",
    "LEFT": "UP"
}

# Clase que relaciona el tipo con su path correspondiente, no esta en la base de datos
class FigurePath:
    def __init__(self, type: typeEnum, path: List[DirectionEnum]):
        self.type = type
        self.path = path

    def __repr__(self):
        return f"FigurePath(type={self.type}, path={self.path})"

# Lista de paths de las figuras (El punto de origen es el bloque de mas a la izquierda y
# si hubiese varios bloques a la izquierda se elige el de mas arriba)
FigurePaths = [
    FigurePath("FIG01", ["DOWN","RIGHT","RIGHT","DOWN"]), #punto de origen izq arriba
    FigurePath("FIG02", ["RIGHT","DOWN","RIGHT","RIGHT"]), #punto de origen izq
    FigurePath("FIG03", ["RIGHT","RIGHT","UP","RIGHT"]), #punto de origen izq
    FigurePath("FIG04", ["DOWN","RIGHT","DOWN","RIGHT"]), #punto de origen izq arriba
    FigurePath("FIG05", ["RIGHT","RIGHT","RIGHT","RIGHT"]), #punto de origen izq
    FigurePath("FIG06", ["DOWN","DOWN","RIGHT","RIGHT"]), #punto de origen izq arriba
    FigurePath("FIG07", ["RIGHT","RIGHT","RIGHT","DOWN"]), #punto de origen izq
    FigurePath("FIG08", ["RIGHT","RIGHT","RIGHT","UP"]), #punto de origen izq
    FigurePath("FIG09", ["RIGHT","DOWN","UP","RIGHT","UP"]), #punto de origen izq
    FigurePath("FIG10", ["DOWN","UP","RIGHT","RIGHT","UP"]), #punto de origen izq arriba
    FigurePath("FIG11", ["DOWN","RIGHT","DOWN","UP","RIGHT"]), #punto de origen izq arriba
    FigurePath("FIG12", ["DOWN","DOWN","UP","RIGHT","RIGHT"]), #punto de origen izq arriba
    FigurePath("FIG13", ["RIGHT","RIGHT","DOWN","UP","RIGHT"]), #punto de origen izq
    FigurePath("FIG14", ["RIGHT","RIGHT","UP","DOWN","RIGHT"]), #punto de origen izq
    FigurePath("FIG15", ["RIGHT","UP","RIGHT","DOWN"]), #punto de origen izq
    FigurePath("FIG16", ["DOWN","RIGHT","RIGHT","UP"]), #punto de origen izq arriba
    FigurePath("FIG17", ["RIGHT","DOWN","UP","UP","DOWN","RIGHT"]), #punto de origen izq
    FigurePath("FIG18", ["RIGHT","DOWN","RIGHT","UP"]), #punto de origen izq
    FigurePath("FIGE01", ["RIGHT","UP","RIGHT"]), #punto de origen izq
    FigurePath("FIGE02", ["RIGHT","DOWN","LEFT"]), #punto de origen izq arriba
    FigurePath("FIGE03", ["RIGHT","DOWN","RIGHT"]), #punto de origen izq
    FigurePath("FIGE04", ["RIGHT","UP","DOWN","RIGHT"]), #punto de origen izq
    FigurePath("FIGE05", ["RIGHT","RIGHT","DOWN"]), #punto de origen izq
    FigurePath("FIGE06", ["RIGHT","RIGHT","RIGHT"]), #punto de origen izq
    FigurePath("FIGE07", ["RIGHT","RIGHT","UP"]) #punto de origen izq
]
