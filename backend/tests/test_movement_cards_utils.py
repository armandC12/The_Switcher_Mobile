import pytest
from unittest.mock import MagicMock
from board.schemas import BoardPosition
from movementCards.utils import MovementCardUtils

@pytest.fixture
def mov_card_utils():
    return MovementCardUtils()

def test_calculate_differences_positive(mov_card_utils):
    pos_from = BoardPosition(pos=(1, 1))
    pos_to = BoardPosition(pos=(4, 5))
    
    x_diff, y_diff = mov_card_utils.calculate_differences(pos_from, pos_to)
    
    assert x_diff == 3
    assert y_diff == 4

def test_calculate_differences_negative(mov_card_utils):
    pos_from = BoardPosition(pos=(5, 5))
    pos_to = BoardPosition(pos=(2, 1))
    
    x_diff, y_diff = mov_card_utils.calculate_differences(pos_from, pos_to)
    
    assert x_diff == 3
    assert y_diff == 4

def test_calculate_differences_zero(mov_card_utils):
    pos_from = BoardPosition(pos=(3, 3))
    pos_to = BoardPosition(pos=(3, 3))
    
    x_diff, y_diff = mov_card_utils.calculate_differences(pos_from, pos_to)
    
    assert x_diff == 0
    assert y_diff == 0