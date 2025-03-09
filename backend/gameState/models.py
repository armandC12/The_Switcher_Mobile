from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database.db import Base
from board.models import ColorEnum
# enum de estados de partida
class StateEnum(str,Enum):
    PLAYING = "PLAYING"
    WAITING = "WAITING"
    FINISHED = "FINISHED"

# modelo del estado de la partida
class GameState(Base):
    __tablename__ = 'game_state'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(SQLAEnum(StateEnum), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', use_alter=True, ondelete='CASCADE'), unique=True, nullable=False)
    current_player = Column(Integer, ForeignKey('players.id', use_alter=True, ondelete='CASCADE'), nullable=True)
    forbidden_color = Column(SQLAEnum(ColorEnum), nullable=True)
    
    game = relationship("Game", back_populates="game_state", uselist=False)
    players = relationship("Player", back_populates="game_state", foreign_keys="[Player.game_state_id]")
    
    __table_args__ = (UniqueConstraint('game_id', name='uq_game_id'),)