import React from "react";

export default function GamesList({ games, currentPage, setCurrentPage, totalPages, loading, selectedGame, setSelectedGame,  }) {

  const handleGameSelect = (game) => {
      setSelectedGame(game); // Select the game if it's not full
  };

  return (
    <>
      {loading ? (
        <div className="text-center text-zinc-200">Loading...</div>
      ) : games && games.length === 0 ? (
        <div className="bg-zinc-950 p-8 rounded-lg shadow-lg border border-zinc-900">
          <div className="h-1/2 text-center justify-center flex flex-col gap-4 bg-zinc-950 text-zinc-300">
            No hay partidas creadas aun.
          </div>
        </div>
      ) : (
        <div className="relative">
          
          

          <div className=" bg-zinc-900 p-8 rounded-lg shadow-md border border-zinc-800 mx-auto">
            <ul className="flex flex-col gap-4">
              {games.map((game) => {
               
                const isFull = game.players_count >= game.max_players;
                const isSelected = selectedGame?.id === game.id;

                return (
                  <li
                    key={game.id}
                    onClick={() => handleGameSelect(game)}
                    className={`bg-zinc-800 group rounded-lg p-6 shadow border  relative transition-all duration-300 cursor-pointer ${
                      isFull
                        ? 'bg-zinc-700 text-zinc-300 cursor-not-allowed opacity-50'
                        : isSelected
                        ? ' border-green-500'
                        : 'border-zinc-800'
                    }`}
                  >
                    {/* Game details spread out with space-between */}
                    <div className="flex justify-between w-full">
                      {/* <div className="flex flex-col"> */}
                        <span className="text-xl font-semibold text-zinc-100">{game.name}</span>
                      {/* </div> */}

                      
                        <span className={`${isFull ? 'text-red-500' : 'text-zinc-300'}`}>
                          {game.players_count} de {game.max_players} jugadores
                        </span>
                        <span className="text-zinc-300">
                          {game.is_private ? 'Privada' : 'Pública'}
                        </span>
                      
                    </div>
                    
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex justify-between items-center mt-6 gap-2">
  <button
    onClick={() => setCurrentPage(currentPage - 1)}
    disabled={currentPage === 1}
    className="bg-green-600 text-white py-2 px-4 sm:py-2 sm:px-6 rounded disabled:opacity-50 hover:bg-green-500 transition-all duration-200 text-xs sm:text-sm md:text-base"
  >
    Anterior
  </button>

  <span className="text-zinc-300 text-center text-xs sm:text-sm md:text-base">
    Página {currentPage} de {totalPages}
  </span>

  <button
    onClick={() => setCurrentPage(currentPage + 1)}
    disabled={currentPage >= totalPages}
    className="bg-green-600 text-white py-2 px-4 sm:py-2 sm:px-6 rounded disabled:opacity-50 hover:bg-green-500 transition-all duration-200 text-xs sm:text-sm md:text-base"
  >
    Siguiente
  </button>
</div>
    </>
  );
}
