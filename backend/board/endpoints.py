import random
from time import sleep

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db
from figureCards.figure_cards_logic import (FigureCardsLogic,
                                            get_fig_cards_logic)
from figureCards.figure_cards_repository import (FigureCardsRepository,
                                                 get_figure_cards_repository)
from player.player_repository import PlayerRepository

from .board_logic import BoardLogic
from .board_repository import BoardRepository
from .models import Board, Box
from .schemas import BoardAndBoxesOut, BoxOut

from connection_manager import manager

board_router = APIRouter(
    prefix="/board",
    tags=['Board']
)

@board_router.get("/{game_id}")
async def get_board(game_id: int, db: Session = Depends(get_db), repo: BoardRepository = Depends()):
    # print("\ngetting board\n")
    # obtener figuras formadas

    result = repo.get_configured_board(game_id, db)
    result_dict = result.model_dump()
    result_dict["formed_figures"] = repo.get_figures(game_id, db)

    return BoardAndBoxesOut(**result_dict)
    # return repo.get_configured_board(game_id, db)

@board_router.patch("/calculate_figures/{game_id}", status_code=status.HTTP_200_OK)
async def get_formed_figures(
    game_id: int,
    db: Session = Depends(get_db),
    fig_cards_logic: FigureCardsLogic = Depends(get_fig_cards_logic)
):
    # sleep(5)
    await fig_cards_logic.get_formed_figures(game_id, db)

    
    message = {"type": f"{game_id}:BOARD_UPDATE"}
    await manager.broadcast(message)
    
    return {"message": "Figures Calculated!"}
