import sqlalchemy
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from .models import FigureCard, typeEnum
from .schemas import FigureCardSchema
from player.models import Player
from game.models import Game

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pdb

class FigureCardsRepository:

    def get_figure_cards(self, game_id: int, player_id: int, db : Session) -> list:
        
        # busco las figure cards asociadas a game_id y player_id
        figure_cards = db.query(FigureCard).filter(FigureCard.player_id == player_id,
                                                    FigureCard.player.has(game_id=game_id)).all()

        if not figure_cards:
            # raise HTTPException(status_code=404, detail="There no figure cards associated with this game and player")
            return []
        # convierto cada elemento en figure_cards a su schema
        figure_cards_list = [FigureCardSchema.model_validate(card) for card in figure_cards]

        return figure_cards_list
    
    def get_figure_card_by_id(self, game_id: int, player_id: int, card_id: int, db : Session) -> FigureCardSchema:
        # busco una figura card especifica segun game_id, player_id y card_id
        try:
            figure_card = db.query(FigureCard).filter(FigureCard.id == card_id, 
                                                        FigureCard.player_id == player_id,
                                                        FigureCard.player.has(game_id=game_id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Figure card not found")

        # convierto la figure card a su schema
        figure_card_schema = FigureCardSchema.model_validate(figure_card)

        return figure_card_schema
    
    def create_figure_card(self, player_id: int, game_id: int, figure: typeEnum, show: bool, blocked: bool, db: Session):
        new_card = FigureCard(
            type=figure,
            show=show,
            game_id= game_id,
            player_id=player_id,
            blocked=blocked, #cambiar  a false
            soft_blocked = False
        )
        db.add(new_card)
        db.commit()
    
    def grab_figure_cards(self, player_id: int, game_id: int, db: Session):
        
        grab = True
        try: 
            db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No game found")

        try: 
            db.query(Player).filter(Player.id == player_id, Player.game_id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found in the game")
        
        figure_cards = db.query(FigureCard).filter(FigureCard.player_id == player_id, 
                                                    FigureCard.game_id == game_id,
                                                    FigureCard.show == True
                                                    ).all()
        
        if any(card.blocked or card.soft_blocked for card in figure_cards):
            grab = False
        
        cards_needed = 3 - len(figure_cards)
        
        if grab and cards_needed > 0:
            hidden_cards = db.query(FigureCard).filter(FigureCard.player_id == player_id, 
                                                        FigureCard.game_id == game_id,
                                                        FigureCard.show == False
                                                        ).limit(cards_needed).all()
            if hidden_cards:
                # Actualizar el atributo show a True para las cartas necesarias
                for card in hidden_cards:
                    card.show = True
                            
                db.commit()
    

    def discard_figure_card(self, figure_card_id: int, db: Session):
        # Fetch figure card by id
        try:
            figure_card = db.query(FigureCard).filter(FigureCard.id == figure_card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail= f"There no figure card associated with this id {figure_card_id}")

        
        # la elimino de la base de datos
        db.delete(figure_card)

        db.commit()

        return {"message": "The figure cards was successfully discarded"}
    
    def unblock_figure_card(self, card_id: int, db: Session):
        try:
            figure_card = db.query(FigureCard).filter(FigureCard.id == card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Figure card not found")
        
        figure_card.blocked = False
        db.commit()
        return {"message": "The figure card was successfully unblocked"}
    
    def soft_block_figure_card(self, card_id: int, db: Session):
        try:
            figure_card = db.query(FigureCard).filter(FigureCard.id == card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Figure card not found")
        
        figure_card.soft_blocked = True
        db.commit()


    def block_figure_card(self, game_id: int, figure_card_id: int, db: Session):
        # Fetch figure card by id
        try:
            figure_card = db.query(FigureCard).filter(FigureCard.id == figure_card_id, FigureCard.game_id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail= f"There no figure card associated with id {figure_card_id} in game {game_id}")

        figure_card.blocked = True

        db.commit()

        return {"message": "The figure cards was successfully blocked"}
    
    def fetch_shown_figure_card_types(self, game_id: int, db: Session):
        
        figure_cards = db.query(FigureCard).filter(FigureCard.game_id == game_id, FigureCard.show == True, FigureCard.blocked == False).all()
        
        if not figure_cards:
            return []
        
        types_set = {figure_card.type for figure_card in figure_cards}
        types_list = list(types_set)
        
        return types_list




def get_figure_cards_repository(figure_cards_repo: FigureCardsRepository = Depends()) -> FigureCardsRepository:
    return figure_cards_repo
