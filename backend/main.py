from enum import Enum
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database.db import init_db


# Rutas
from game.endpoints import game_router
from board.endpoints import board_router
from gameState.endpoints import game_state_router
from movementCards.endpoints import movement_cards_router
from figureCards.endpoints import figure_cards_router
from player.endpoints import player_router

init_db()

#Connection Manager
from connection_manager import manager

app = FastAPI()

# Permitir conexiones externas
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Registrar rutas
app.include_router(game_router)
app.include_router(game_state_router)
app.include_router(board_router)
app.include_router(movement_cards_router)
app.include_router(figure_cards_router)
app.include_router(player_router)

@app.get("/")
async def root():
    return {"message": "El Switcher"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)



