from .models import turnEnum
import random
from .player_repository import PlayerRepository 
from sqlalchemy.orm import Session
from database.db import get_db
from fastapi import Depends

def get_player_logic(player_repo: PlayerRepository = Depends()):
    return PlayerLogic(player_repo)

class PlayerLogic:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    def assign_random_turns(self, players, db: Session):
        randomTurns = random.sample(range(1, len(players) + 1), len(players))
        turnMapping = {1: turnEnum.PRIMERO, 2: turnEnum.SEGUNDO, 3: turnEnum.TERCERO, 4: turnEnum.CUARTO}
        
        firstPlayer = None
        
        for player, turn in zip(players, randomTurns):
            self.player_repo.assign_turn_player(player.game_id, player.id, turnMapping[turn], db)
            if turn == 1:
                firstPlayer = player
        
        return firstPlayer.id