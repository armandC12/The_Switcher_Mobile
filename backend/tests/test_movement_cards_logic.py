from pydantic import ValidationError
import pytest
from unittest.mock import MagicMock, patch
from movementCards.movement_cards_logic import MovementCardLogic
from movementCards.models import typeEnum
from movementCards.movement_cards_repository import MovementCardsRepository

from board.schemas import BoardPosition
from sqlalchemy.orm import Session
from database.db import get_db
from main import app 
from fastapi import HTTPException
from fastapi.testclient import TestClient


client = TestClient(app)


# Mock database
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_mov_card_repo():
    return MagicMock(spec=MovementCardsRepository)


@pytest.fixture
def mov_cards_logic(mock_mov_card_repo):
    mock_player_repo = MagicMock()
    mock_utils = MagicMock()
    return MovementCardLogic(mov_card_repo=mock_mov_card_repo, player_repo=mock_player_repo, utils= mock_utils)

    
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db


def test_create_mov_deck_success(mov_cards_logic, mock_db):
    game_id = 1

    # Mock players in the game
    mock_player_1 = MagicMock()
    mock_player_1.id = 1
    mock_player_2 = MagicMock()
    mock_player_2.id = 2

    # Me aseguro que devuelva una lista de jugadores
    mov_cards_logic.player_repo.get_players_in_game.return_value = [mock_player_1, mock_player_2]

    # Mock movement cards 
    mock_movement_card_1 = MagicMock()
    mock_movement_card_1.id = 101
    mock_movement_card_2 = MagicMock()
    mock_movement_card_2.id = 102
    mock_movement_card_3 = MagicMock()
    mock_movement_card_3.id = 103

    # Mockeo la respuesta de get_movement_deck
    mov_cards_logic.mov_card_repo.get_movement_deck.return_value = [
        mock_movement_card_1,
        mock_movement_card_2,
        mock_movement_card_3
    ] * 17  # Para tener mas de 6 cartas

    with patch('random.shuffle', lambda x: x), patch('random.sample', lambda x, y: x[:y]):
        response = mov_cards_logic.create_mov_deck(game_id, mock_db)

    assert response == {"message": "Movement deck created and assigned to players"}

    # expected_calls = [
    #     ((game_id, typeEnum.DIAGONAL_CONT, mock_db),),
    #     ((game_id, typeEnum.DIAGONAL_ESP, mock_db),),
    #     ((game_id, typeEnum.EN_L_DER, mock_db),),
    #     ((game_id, typeEnum.EN_L_IZQ, mock_db),),
    #     ((game_id, typeEnum.LINEAL_AL_LAT, mock_db),),
    #     ((game_id, typeEnum.LINEAL_CONT, mock_db),),
    #     ((game_id, typeEnum.LINEAL_ESP, mock_db),)      
    # ] * 7

    assert mov_cards_logic.mov_card_repo.create_movement_card.call_count == 40

    assert mov_cards_logic.mov_card_repo.assign_mov_card.call_count == 6  # 3 cartas por player

    
def test_create_mov_deck_no_players(mov_cards_logic, mock_db):
    game_id = 1

    # Me aseguro que devuelva una lista de jugadores vacia
    mov_cards_logic.player_repo.get_players_in_game.return_value = []

        # Mock movement cards 
    mock_movement_card_1 = MagicMock()
    mock_movement_card_1.id = 101
    mock_movement_card_2 = MagicMock()
    mock_movement_card_2.id = 102
    mock_movement_card_3 = MagicMock()
    mock_movement_card_3.id = 103

    # Mockeo la respuesta de get_movement_deck
    mov_cards_logic.mov_card_repo.get_movement_deck.return_value = [
        mock_movement_card_1,
        mock_movement_card_2,
        mock_movement_card_3
    ] * 17  # Para tener mas de 6 cartas

    with patch('random.shuffle', lambda x: x), patch('random.sample', lambda x, y: x[:y]):
        response = mov_cards_logic.create_mov_deck(game_id, mock_db)

    assert response == {"message": "Movement deck was not created because there are no players in game"}
    
def test_validate_movement_valid(mov_cards_logic, mock_db):
    card_id = 1 
    pos_from = BoardPosition(pos=(0, 5)) 
    pos_to = BoardPosition(pos=(0, 3))
    
    mov_cards_logic.mov_card_repo.get_movement_card_type.return_value = typeEnum.LINEAL_ESP
    mov_cards_logic.validate_lineal_esp = MagicMock(return_value=None)
    
    mov_cards_logic.validate_movement(card_id, pos_from, pos_to, mock_db)
    
    mov_cards_logic.mov_card_repo.get_movement_card_type.assert_called_once_with(card_id, mock_db)
    mov_cards_logic.validate_lineal_esp.assert_called_once_with(pos_from, pos_to)
    
def test_validate_movement_invalid_type(mov_cards_logic, mock_db):
    card_id = 1 
    pos_from = BoardPosition(pos=(0, 5))
    pos_to = BoardPosition(pos=(0, 3))
    
    mov_cards_logic.mov_card_repo.get_movement_card_type.return_value = "Invalid type"
    
    with pytest.raises(HTTPException) as exc_info:
        mov_cards_logic.validate_movement(card_id, pos_from, pos_to, mock_db)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid movement type"
    
def test_validate_movement_invalid_position(mov_cards_logic, mock_db):
    card_id = 1 
    pos_from = (0, 8)
    pos_to = (10, 3)
    
    
    with pytest.raises(TypeError) as exc_info:
        mov_cards_logic.validate_movement(card_id, pos_from, pos_to, mock_db)
    
    assert str(exc_info.value) == "pos_from and pos_to must be instances of BoardPosition"
    
def test_validate_lineal_cont_valid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    # Movimiento valido
    pos_to = BoardPosition(pos=(0, 1))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (0,1)
    result = mov_cards_logic.validate_lineal_cont(pos_from, pos_to)
    
    assert result == True

def test_validate_lineal_cont_invalid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    # movimiento invalido
    pos_to = BoardPosition(pos=(1, 2))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,2)
    result = mov_cards_logic.validate_lineal_cont(pos_from, pos_to)
    
    assert result == False

def test_validate_lineal_cont_invalid_two_jumps(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    # movimiento invalido
    pos_to = BoardPosition(pos=(0, 2))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (0,2)
    result = mov_cards_logic.validate_lineal_cont(pos_from, pos_to)
    
    assert result == False
    
def test_validate_lineal_esp_valid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    #Movimiento valido, salto de 2
    pos_to = BoardPosition(pos=(0, 2))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (0,2)
    result = mov_cards_logic.validate_lineal_esp(pos_from, pos_to)
    
    assert result == True

def test_validate_lineal_esp_invalid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    #Movimiento invalido, salto de 3
    pos_to = BoardPosition(pos=(1, 3))
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,3)
    result = mov_cards_logic.validate_lineal_esp(pos_from, pos_to)
    
    assert result == False
    
def test_validate_diagonal_cont_valid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    # movimiento valido
    pos_to = BoardPosition(pos=(1, 1))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,1)
    result = mov_cards_logic.validate_diagonal_cont(pos_from, pos_to)
    
    assert result == True
    
def test_validate_diagonal_cont_invalid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    # Movimiento invalido, no es adyacente
    pos_to = BoardPosition(pos=(2, 2))
    
    mov_cards_logic.utils.calculate_differences.return_value = (2,2)
    result = mov_cards_logic.validate_diagonal_cont(pos_from, pos_to)
    
    assert result == False
    
def test_validate_diagonal_esp_valid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    #Movimiento valido,diagonal con un espacio
    pos_to = BoardPosition(pos=(2, 2))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (2,2)
    result = mov_cards_logic.validate_diagonal_esp(pos_from, pos_to)
    
    assert result == True

def test_validate_diagonal_esp_invalid(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    #Movimiento invalido
    pos_to = BoardPosition(pos=(3, 3))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (3,3)
    result = mov_cards_logic.validate_diagonal_esp(pos_from, pos_to)
    
    assert result == False
    
def test_validate_en_l_der_valid_case1(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    #Movimiento en L hacia la derecha valido (un lugar en x, dos en y)
    pos_to = BoardPosition(pos=(1, 2))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,2)
    result = mov_cards_logic.validate_en_l_der(pos_from, pos_to)
    
    assert result == True

def test_validate_en_l_der_valid_case2(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 2))
    #Movimiento en L hacia la derecha valido (dos lugares en y, un lugar en x)
    pos_to = BoardPosition(pos=(1, 4))
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,2)
    result = mov_cards_logic.validate_en_l_der(pos_from, pos_to)
    
    assert result == True

def test_validate_en_l_der_invalid_case1(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    #Movimiento invalido, no es en forma de L
    pos_to = BoardPosition(pos=(3, 3))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (3,3)
    result = mov_cards_logic.validate_en_l_der(pos_from, pos_to)
    
    assert result == False

def test_validate_en_l_der_invalid_case2(mov_cards_logic):
    pos_from = BoardPosition(pos=(2, 2))
    #Movimiento invalido, en L hacia la izquierda
    pos_to = BoardPosition(pos=(0, 1))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (2,1)
    result = mov_cards_logic.validate_en_l_der(pos_from, pos_to)
    
    assert result == False

def test_validate_en_l_izq_valid_case1(mov_cards_logic):
    pos_from = BoardPosition(pos=(2, 2))
    #Movimiento valido, un lugar en y, dos en x 
    pos_to = BoardPosition(pos=(0, 1))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (2,1)
    result = mov_cards_logic.validate_en_l_izq(pos_from, pos_to)
    
    assert result == True

def test_validate_en_l_izq_valid_case2(mov_cards_logic):
    pos_from = BoardPosition(pos=(3, 3))
    #dos lugares en y , uno en x
    pos_to = BoardPosition(pos=(4, 1))
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,2)
    result = mov_cards_logic.validate_en_l_izq(pos_from, pos_to)
    
    assert result == True

def test_validate_en_l_izq_invalid_case1(mov_cards_logic):
    pos_from = BoardPosition(pos=(0, 0))
    #Invalido, no es en forma de L
    pos_to = BoardPosition(pos=(4, 5))      
    
    mov_cards_logic.utils.calculate_differences.return_value = (4,5)
    result = mov_cards_logic.validate_en_l_izq(pos_from, pos_to)
    
    assert result == False

def test_validate_en_l_izq_invalid_case2(mov_cards_logic):
    pos_from = BoardPosition(pos=(3, 3))
    # Invalido, es en L pero hacia la derecha
    pos_to = BoardPosition(pos=(4, 5))
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,2)
    result = mov_cards_logic.validate_en_l_izq(pos_from, pos_to)
    
    assert result == False
    
def test_validate_lineal_al_lat_valid_case1(mov_cards_logic):
    pos_from = BoardPosition(pos=(2, 2))
    # Valido, al borde de la misma fila
    pos_to = BoardPosition(pos=(2, 0))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (0,2)
    result = mov_cards_logic.validate_lineal_al_lat(pos_from, pos_to)
    
    assert result == True

def test_validate_lineal_al_lat_valid_case2(mov_cards_logic):
    pos_from = BoardPosition(pos=(3, 3))
    # Valido, al borde de la misma columna
    pos_to = BoardPosition(pos=(0, 3))
    
    mov_cards_logic.utils.calculate_differences.return_value = (3,0)  
    result = mov_cards_logic.validate_lineal_al_lat(pos_from, pos_to)
    
    assert result == True

def test_validate_lineal_al_lat_invalid_case1(mov_cards_logic):
    pos_from = BoardPosition(pos=(1, 1))
    # Invalido, al borde de otra fila
    pos_to = BoardPosition(pos=(2, 5))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (1,4)    
    result = mov_cards_logic.validate_lineal_al_lat(pos_from, pos_to)
    
    assert result == False

def test_validate_lineal_al_lat_invalid_case2(mov_cards_logic):
    pos_from = BoardPosition(pos=(4, 4))
    # Invalido, a una posición anterior al borde
    pos_to = BoardPosition(pos=(4, 3))  
    
    mov_cards_logic.utils.calculate_differences.return_value = (0,1)
    result = mov_cards_logic.validate_lineal_al_lat(pos_from, pos_to)
    
    assert result == False
    