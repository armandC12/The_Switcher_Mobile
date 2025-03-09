import React from 'react'
import CardsFigure from './CardsFigure'
import OthersCardsMovement from './OthersCardsMovement'


export default function PlayerPanel({ game, panelOwner, playerId, name, setSelectedCardFigure, selectedCardFigure, turnBorder, selectedBlockCard, setSelectedBlockCard, resetMovement, resetFigureSelection, resetBlock, getTurnInfo, currentTurn }) {
  return (
    <>
      {/* <h2 className="text-xl text-center mb-5">{name}'s figures</h2> */}
      <CardsFigure 
        name={name}
        gameId={game} 
        playerId={playerId} 
        setSelectedCardFigure={setSelectedCardFigure} 
        selectedCardFigure={selectedCardFigure} 
        turnBorder={turnBorder}
        currentTurn={currentTurn}
        panelOwner={panelOwner}
        getTurnInfo={getTurnInfo}
        resetMovement={resetMovement}
        selectedBlockCard={selectedBlockCard}
        setSelectedBlockCard={setSelectedBlockCard}
        resetFigureSelection={resetFigureSelection}
        resetBlock={resetBlock}
      />
      <OthersCardsMovement
        gameId={game}
        playerId={panelOwner}
      />
    </>
  )
}