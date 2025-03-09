import React from "react";
import { ImBlocked } from "react-icons/im";

const getColorBox = (color) => {
  switch (color) {
    case 'GREEN':
      return 'bg-gradient-to-br from-green-400 to-green-600';
    case 'BLUE':
      return 'bg-gradient-to-br from-blue-400 to-blue-600';
    case 'RED':
      return 'bg-gradient-to-br from-red-400 to-red-600';
    case 'YELLOW':
      return 'bg-gradient-to-br from-yellow-400 to-yellow-600';
    default:
      return 'bg-gradient-to-br from-gray-400 to-gray-600';
  }
};

const getColorForbiddenIcon = (color) => {
  switch (color) {
    case 'GREEN':
      return 'text-green-900';
    case 'BLUE':
      return 'text-blue-900';
    case 'RED':
      return 'text-red-900';
    case 'YELLOW':
      return 'text-yellow-900';
    default:
      return 'text-gray-900';
  }
};

export default function GameBoard({boxes, blockedColor, currentTurn, playerId,
                                  selectedCardFigure, selectedBoardFigure, setSelectedBoardFigure,
                                  selectedMovementCard, setSelectMovementPosition, selectedMovementPositions, figuresFormed, syncEffect, selectedBlockCard}) {

  const handleSelectFigure = (box) => {
    let boxFound = null;
    let indexFigureFound = -1;
    
    figuresFormed.find((figure, index) => {
      boxFound = figure.find(
        (elem) => {
          const isMatch = elem.pos_x === box.pos_x &&
          elem.pos_y === box.pos_y &&
          elem.color === box.color;

          return isMatch;
        }
      );

      indexFigureFound = index;
      return boxFound;
    });

    if (!boxFound) {
      console.error("Box does not belong to a valid formed figure");
      return;
    }
    setSelectedBoardFigure(figuresFormed[indexFigureFound]);
  };

  const handleSelectMovement = (box) => {
    if (!selectedMovementCard) {
      return;
    }

    const position = { x: box.pos_x, y: box.pos_y };

    const isAlreadySelected = selectedMovementPositions.some(
      (pos) => pos.x === position.x && pos.y === position.y
    );

    let newSelectedMovementPositions;

    if (isAlreadySelected) {
      // Si la casilla ya está seleccionada, removerla
      newSelectedMovementPositions = selectedMovementPositions.filter(
        (pos) => pos.x !== position.x || pos.y !== position.y
      );
    } else if (selectedMovementPositions.length < 2) {
      // Si aún no se han seleccionado dos casillas, agregar la nueva casilla
      newSelectedMovementPositions = [...selectedMovementPositions, position];
    } else {
      // Si ya se han seleccionado dos casillas, reemplazar la más antigua (la primera)
      newSelectedMovementPositions = [
        selectedMovementPositions[1],
        position                      // nueva posicion seleccionada
      ];
    }

    setSelectMovementPosition(newSelectedMovementPositions); // Pasar las posiciones seleccionadas a ActiveGame
  };

  return (
    // <div className="relative flex h-[600px] w-[600px] flex-col items-center justify-center rounded-lg shadow-xl border-4 border-zinc-700 bg-zinc-800 p-4">
    <div className="relative flex w-full h-full sm:w-[600px] sm:h-[600px] aspect-square flex-col items-center justify-center rounded-lg shadow-xl border-4 border-zinc-700 bg-zinc-800 p-1 sm:p-4">
      <style jsx global>{`
        @keyframes glass-shine {
          0% { transform: translateX(-150%) translateY(-150%); }
          100% { transform: translateX(150%) translateY(150%); }
        }
        .shine-effect::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 150%;
          height: 150%;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0) 30%, rgba(255, 255, 255, 0.6) 50%, rgba(255, 255, 255, 0) 70%);
          transform: translateX(-150%) translateY(-150%);
          animation: glass-shine 5s ease-in-out infinite;
          pointer-events: none;
        }
        @keyframes fast-pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        .animate-fast-pulse {
          animation: fast-pulse 0.3s ease-in-out 3;
        }
      `}</style>
      {/* <div className="grid grid-cols-6 grid-rows-6 gap-2 w-full h-full"> */}
      <div className="grid grid-cols-6 grid-rows-6 gap-1 sm:gap-2 w-full h-full">
        {boxes.length > 0 &&
          boxes.map((row, rowIndex) =>
            row.map((box, colIndex) => {
              const isSelectedFigure = selectedBoardFigure.some(
                (selectedBox) =>
                  selectedBox.pos_x === box.pos_x &&
                  selectedBox.pos_y === box.pos_y &&
                  selectedBox.color === box.color
              );
              const isSelectedMovement = selectedMovementPositions.some(
                (pos) => pos.x === box.pos_x && pos.y === box.pos_y
              );
  
              return (
                <button
                  disabled={blockedColor === box.color && selectedCardFigure !== null}
                  onClick={
                    ((selectedCardFigure || selectedBlockCard) && !selectedMovementCard)
                      ? () => handleSelectFigure(box)
                      : () => handleSelectMovement(box)
                  }
                  data-testid={`box-${box.pos_x}-${box.pos_y}`}
                  key={`${rowIndex}-${colIndex}`}
                  className={`relative overflow-hidden rounded w-full h-full 
                    ${getColorBox(box.color)}
                    ${isSelectedFigure ? 'animate-pulse' : ''}
                    ${isSelectedMovement ? 'brightness-75 animate-pulse' : 'brightness-100'}
                    ${(!selectedCardFigure && !selectedMovementCard && !selectedBlockCard) ? 'cursor-default' : 'cursor-pointer'}`}
                  style={{ gridColumn: box.pos_x + 1, gridRow: box.pos_y + 1 }}
                >
                  {/* Blocked Overlay */}
                  {blockedColor === box.color && (
                    <div className="absolute inset-0 flex items-center justify-center ">
                      <ImBlocked className={`${getColorForbiddenIcon(box.color)} w-8 h-8 font-extrabold`} />
                    </div>
                  )}
                  {box.highlighted && blockedColor !== box.color && currentTurn === playerId && syncEffect && (
                    <div className="shine-effect"></div>
                  )}                </button>
              );
            })
          )
        }
      </div>
    </div>
  );
}  