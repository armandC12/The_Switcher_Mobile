import { render, screen } from "@testing-library/react";
import GameBoard from "@/components/ui/GameBoard";
import { MemoryRouter } from "react-router-dom";

const mockData = {
  boxes: [
    [
      { pos_x: 0, pos_y: 0, color: "RED", highlighted: true },
      { pos_x: 1, pos_y: 0, color: "RED", highlighted: true },
      { pos_x: 2, pos_y: 0, color: "RED", highlighted: true },
      { pos_x: 3, pos_y: 0, color: "BLUE", highlighted: false },
      { pos_x: 4, pos_y: 0, color: "YELLOW", highlighted: false },
      { pos_x: 5, pos_y: 0, color: "GREEN", highlighted: false }
    ],
    [
      { pos_x: 0, pos_y: 1, color: "GREEN", highlighted: false },
      { pos_x: 1, pos_y: 1, color: "YELLOW", highlighted: false },
      { pos_x: 2, pos_y: 1, color: "RED", highlighted: true },
      { pos_x: 3, pos_y: 1, color: "BLUE", highlighted: false },
      { pos_x: 4, pos_y: 1, color: "GREEN", highlighted: false },
      { pos_x: 5, pos_y: 1, color: "RED", highlighted: false }
    ],
    [
      { pos_x: 0, pos_y: 2, color: "BLUE", highlighted: true },
      { pos_x: 1, pos_y: 2, color: "YELLOW", highlighted: false },
      { pos_x: 2, pos_y: 2, color: "GREEN", highlighted: false },
      { pos_x: 3, pos_y: 2, color: "RED", highlighted: false },
      { pos_x: 4, pos_y: 2, color: "YELLOW", highlighted: false },
      { pos_x: 5, pos_y: 2, color: "GREEN", highlighted: false }
    ],
    [
      { pos_x: 0, pos_y: 3, color: "BLUE", highlighted: true },
      { pos_x: 1, pos_y: 3, color: "RED", highlighted: false },
      { pos_x: 2, pos_y: 3, color: "GREEN", highlighted: false },
      { pos_x: 3, pos_y: 3, color: "YELLOW", highlighted: false },
      { pos_x: 4, pos_y: 3, color: "BLUE", highlighted: false },
      { pos_x: 5, pos_y: 3, color: "RED", highlighted: false }
    ],
    [
      { pos_x: 0, pos_y: 4, color: "BLUE", highlighted: true },
      { pos_x: 1, pos_y: 4, color: "BLUE", highlighted: true },
      { pos_x: 2, pos_y: 4, color: "RED", highlighted: false },
      { pos_x: 3, pos_y: 4, color: "YELLOW", highlighted: false },
      { pos_x: 4, pos_y: 4, color: "GREEN", highlighted: false },
      { pos_x: 5, pos_y: 4, color: "YELLOW", highlighted: false }
    ],
    [
      { pos_x: 0, pos_y: 5, color: "GREEN", highlighted: false },
      { pos_x: 1, pos_y: 5, color: "YELLOW", highlighted: false },
      { pos_x: 2, pos_y: 5, color: "RED", highlighted: false },
      { pos_x: 3, pos_y: 5, color: "BLUE", highlighted: false },
      { pos_x: 4, pos_y: 5, color: "GREEN", highlighted: false },
      { pos_x: 5, pos_y: 5, color: "RED", highlighted: false }
    ]
  ],
  figuresFormed: [
    [
      { pos_x: 0, pos_y: 2, color: "BLUE", highlighted: true },
      { pos_x: 0, pos_y: 3, color: "BLUE", highlighted: true },
      { pos_x: 0, pos_y: 4, color: "BLUE", highlighted: true },
      { pos_x: 1, pos_y: 4, color: "BLUE", highlighted: true }
    ],
  ]
};

const mockBlockedColor = null;
const mockCurrentTurn = 1;
const mockPlayerId = 1;
const mockSelectedCardFigure = null;
const mockSetSelectedBoardFigure = vi.fn();
const mockSelectedMovementCard = null;
const mockSetSelectMovementPosition = vi.fn();
const mockSelectedMovementPositions = [];
const mockFiguresFormed = mockData.figuresFormed;
const mockSyncEffect = true;

describe('Creación del tablero', () => {
  it('Si le llegan 36 casillas en el formato pactado, las renderiza', () => {
    render(
      <MemoryRouter>
        <GameBoard
          boxes={mockData.boxes}
          blockedColor={mockBlockedColor}
          currentTurn={mockCurrentTurn}
          playerId={mockPlayerId}
          selectedCardFigure={mockSelectedCardFigure}
          selectedBoardFigure={mockFiguresFormed[0]}
          setSelectedBoardFigure={mockSetSelectedBoardFigure}
          selectedMovementCard={mockSelectedMovementCard}
          setSelectMovementPosition={mockSetSelectMovementPosition}
          selectedMovementPositions={mockSelectedMovementPositions}
          figuresFormed={mockFiguresFormed}
          syncEffect={mockSyncEffect}
        />
      </MemoryRouter>
    );

    mockData.boxes.flat().forEach((box) => {
      const boxElement = screen.getByTestId(`box-${box.pos_x}-${box.pos_y}`);

      expect(boxElement).toBeInTheDocument();

      if (!box.highlighted) {
        expect(boxElement).not.toHaveClass('shine-effect');
      }
    });
  });
});
