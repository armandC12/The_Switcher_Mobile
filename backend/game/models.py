from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.db import Base

# Modelo de partida
class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    max_players = Column(Integer, nullable=False)
    min_players = Column(Integer, nullable=False)
    is_private = Column(Boolean, default=False) 
    password = Column(String, nullable=True)

    game_state = relationship("GameState", back_populates="game", uselist=False, passive_deletes=True)
    players = relationship("Player", back_populates="game", passive_deletes=True, cascade='all, delete')
    boxes = relationship("Box", back_populates="game", passive_deletes=True)
    board = relationship("Board", back_populates="game", passive_deletes=True)
    movement_cards = relationship("MovementCard", back_populates="game", passive_deletes=True)
    figure_cards = relationship("FigureCard", back_populates="game", passive_deletes=True)
    partial_movements = relationship("PartialMovements", back_populates="game", passive_deletes=True)

    def players_count(self):
        return len(self.players)
    
    