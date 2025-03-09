import random
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound

from .models import MovementCard
from .schemas import MovementCardSchema, typeEnum

from player.models import Player
from game.models import Game


class MovementCardsRepository:
    
    def get_players_movement_cards(self, game_id: int, db : Session) -> list:
        try:
            db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = f"Game not found")
        
        movement_cards = db.query(MovementCard).filter( 
                                                        MovementCard.game_id == game_id,
                                                        MovementCard.player_id.is_not(None)
                                                      ).all()

        if not movement_cards:
            raise HTTPException(status_code=404, detail="There no movement cards associated with this game")

        movement_cards_list = [MovementCardSchema.model_validate(card) for card in movement_cards]

        return movement_cards_list

    def get_movement_cards(self, game_id: int, player_id: int, db : Session) -> list:
        # Fetch figure cards associated with the player and game
        movement_cards = db.query(MovementCard).filter(MovementCard.player_id == player_id,
                                                    MovementCard.player.has(game_id=game_id)).all()

        if not movement_cards:
            raise HTTPException(status_code=404, detail="There no movement cards associated with this game and player")

        # Convert movement cards to a list of schemas
        movement_cards_list = [MovementCardSchema.model_validate(card) for card in movement_cards]

        return movement_cards_list
    

    def get_movement_card_by_id(self, game_id: int, player_id: int, card_id: int, db : Session) -> MovementCardSchema:
        
        # Fetch the specific movement card by its id, player_id and game_id
        try:
            movement_card = db.query(MovementCard).filter(MovementCard.id == card_id, 
                                                        MovementCard.player_id == player_id,
                                                        MovementCard.player.has(game_id=game_id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Movement card not found")

        # Convert the movement card to a schema
        movement_card_schema = MovementCardSchema.model_validate(movement_card)

        return movement_card_schema


    def create_movement_card(self, game_id: int, type: typeEnum, position: int, db : Session):
        if type not in typeEnum.__members__:
            raise HTTPException(status_code = 400, detail = f"Incorrect type for movement card: {type}")
        
        # Fetch the specifc game by its id
        try:
            game = db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = f"Game with id {game_id} not found")
        
        new_card = MovementCard(
            description = "",
            used = False,
            game_id = game_id,
            type = type, 
            position = position
        )

        db.add(new_card)
        db.commit()


    def get_movement_deck(self, game_id: int, db : Session) -> list:
        # Fetch figure cards associated with the game
        movement_cards = db.query(MovementCard).filter(MovementCard.game_id == game_id,
                                                    MovementCard.player_id.is_(None)).all()

        if not movement_cards:
            raise HTTPException(status_code=404, detail="There no movement cards associated with this game")

        # Convert movement deck of cards to a list of schemas
        movement_cards_deck = [MovementCardSchema.model_validate(card) for card in movement_cards]

        return movement_cards_deck
    

    def assign_mov_card(self, mov_card_id: int, player_id: int, db : Session) -> list:
        # Fetch figure cards associated with the player and game
        try:
            mov_card = db.query(MovementCard).filter(MovementCard.id == mov_card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="There no movement cards associated with this game")

        try:
            player = db.query(Player).filter(Player.id == player_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="no player with specified id")
        
        mov_card.player = player
        mov_card.position = None
        db.commit()

        return mov_card
    
    def grab_mov_cards(self, player_id: int, game_id: int,db: Session):
        try: 
            db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No game found")
        
        try: 
            db.query(Player).filter(Player.id == player_id, Player.game_id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
        
        movement_cards = db.query(MovementCard).filter(
                                                        MovementCard.player_id == player_id,
                                                        MovementCard.game_id==game_id, 
                                                        MovementCard.used == False
                                                       ).all()
        
        cards_needed = 3 - len(movement_cards)
        
        if cards_needed > 0:
            #Obtengo cartas no asignadas a un jugador que no hayan sido usadas
            unassigned_cards = db.query(MovementCard).filter(
                                                                MovementCard.player_id.is_(None),
                                                                MovementCard.game_id == game_id,
                                                                MovementCard.used == False,
                                                                MovementCard.position.is_not(None),
                                                            ).order_by(MovementCard.position).limit(cards_needed).all()
            #Si no hay suficientes, volvemos a armar el mazo de mov con las cartas ya usadas
            if len(unassigned_cards) < cards_needed:
                self.reshuffle_movement_deck(game_id, db)
                #Obtengo las cartas necesarias para asignarle al jugador
                unassigned_cards = db.query(MovementCard).filter(
                                                                MovementCard.player_id.is_(None),
                                                                MovementCard.game_id == game_id,
                                                                MovementCard.used == False
                                                            ).order_by(MovementCard.position).limit(cards_needed).all()

            #Se las asigno al jugador    
            for card in unassigned_cards:
                card.player_id = player_id
                card.position = None
            
            db.commit()
            
        

    def discard_mov_card(self, mov_card_id: int, db: Session):
        # Fetch movement card by id
        try:
            mov_card = db.query(MovementCard).filter(MovementCard.id == mov_card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail= f"There no movement cards associated with this id {mov_card_id}")

        # la denoto como recien usada para no volver a darla
        mov_card.used = True

        # la mando al mazo, no le pertence a ningun jugador
        mov_card.player_id = None
                                
        mov_card.position = None

        db.commit()

        return {"message": "The movement card with {mov_card_id} was successfully deleted."}


    def reshuffle_movement_deck(self, game_id : int, db: Session):
        used_cards = db.query(MovementCard).filter(
                                                    MovementCard.player_id.is_(None),
                                                    MovementCard.game_id == game_id
                                                  ).all()

        if not used_cards:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No used cards available to reshuffle")        
        
        random.shuffle(used_cards)
        for index, card in enumerate(used_cards):
            card.used = False
            card.position = index
        
        db.commit()
    
    def mark_card_in_player_hand(self, card_id: int, db: Session):
        try:
            movement_card = db.query(MovementCard).filter(MovementCard.id == card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No movement card found")
        
        movement_card.used = False
        db.commit()
        
    def get_movement_card_type(self, card_id: int, db: Session) -> typeEnum:
        try:
            movement_card = db.query(MovementCard).filter(MovementCard.id == card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No movement card found")
        
        return typeEnum(movement_card.type)
    
    def mark_card_partially_used(self, card_id: int, db: Session):
        try:
            movement_card = db.query(MovementCard).filter(MovementCard.id == card_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No movement card found")
        
        movement_card.used = True
        db.commit()
        
    

    def discard_all_player_partially_used_cards(self, player_id: int, db: Session):
            partially_used_cards = db.query(MovementCard).filter(
                MovementCard.player_id == player_id,
                MovementCard.used == True
            ).all()

            for card in partially_used_cards:
                card.player_id = None
                card.position = None

            db.commit()  
        
        
def get_movement_cards_repository(movement_cards_repo: MovementCardsRepository = Depends()) -> MovementCardsRepository:
    return movement_cards_repo

