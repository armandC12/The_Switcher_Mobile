from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.db import Base
from game.models import Game
from gameState.models import GameState
from figureCards.models import FigureCard
from movementCards.models import MovementCard

# enum de los turnos
class turnEnum(str,Enum):
    PRIMERO = "PRIMERO"
    SEGUNDO = "SEGUNDO"
    TERCERO = "TERCERO"
    CUARTO  = "CUARTO"

# modelo de jugador
class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', use_alter=True, ondelete='CASCADE'))
    game_state_id = Column(Integer, ForeignKey('game_state.id', use_alter=True, ondelete='CASCADE'), nullable=True)
    turn = Column(SQLAEnum(turnEnum), nullable=True)
    host = Column(Boolean, nullable=False)
    winner = Column(Boolean, nullable=False, unique=False)

    game_state = relationship("GameState", back_populates="players", foreign_keys="[Player.game_state_id]")
    game = relationship("Game", back_populates="players")
    figure_cards = relationship("FigureCard", back_populates="player", cascade="all")
    movement_cards = relationship("MovementCard", back_populates="player", cascade="all")
    partial_movements = relationship("PartialMovements", back_populates="player", cascade="all")