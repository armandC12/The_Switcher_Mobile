from board.schemas import BoardPosition

class MovementCardUtils:
    def calculate_differences(self, pos_from: BoardPosition, pos_to: BoardPosition) -> tuple:
        x_diff = abs(pos_to.pos[0] - pos_from.pos[0])
        y_diff = abs(pos_to.pos[1] - pos_from.pos[1])
        return x_diff, y_diff