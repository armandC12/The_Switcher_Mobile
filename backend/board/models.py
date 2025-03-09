from enum import Enum
from sqlalchemy import Boolean, Column, Integer, String, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base
from figureCards.models import typeEnum

class ColorEnum(Enum):
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"

class Box(Base):
    __tablename__ = 'boxes'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    color = Column(SQLAEnum(ColorEnum), nullable=False)
    pos_x = Column(Integer, nullable=False)
    pos_y = Column(Integer, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', use_alter=True, ondelete='CASCADE'), nullable=False)
    board_id = Column(Integer, ForeignKey('boards.id', use_alter=True, ondelete='CASCADE'), nullable=False)
    highlight = Column(Boolean, nullable=False)
    figure_id = Column(Integer, nullable=True)
    figure_type = Column(SQLAEnum(typeEnum), nullable=True)


    game = relationship("Game", back_populates="boxes")
    board = relationship("Board", back_populates="boxes")  


class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id', use_alter=True, ondelete='CASCADE'), nullable=False)
    
    game = relationship("Game", back_populates="board")
    boxes = relationship("Box", back_populates="board")  
