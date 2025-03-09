from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database.db import Base

class PartialMovements(Base):
    __tablename__ = 'partial_movements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pos_from_x = Column(Integer, nullable=False)
    pos_from_y = Column(Integer, nullable=False)
    pos_to_x = Column(Integer, nullable=False)
    pos_to_y = Column(Integer, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id', use_alter=True, ondelete='CASCADE'), nullable=True)
    mov_card_id = Column(Integer, ForeignKey('movement_cards.id'), nullable=False)

    game = relationship("Game", back_populates="partial_movements")
    player = relationship("Player", back_populates="partial_movements")
    movement_card = relationship("MovementCard", back_populates="partial_movements")