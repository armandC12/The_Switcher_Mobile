import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCrown } from "@fortawesome/free-solid-svg-icons";

// Array of colors for player names
const colors = ["text-red-400", "text-blue-400", "text-green-400", "text-yellow-400"];

export default function PlayersList({ players, maxPlayers }) {
  // Function to assign a color based on the player's index
  const getPlayerColor = (index) => {
    return colors[index % colors.length]; // Cycle through the colors array
  };

  return (
    <div className="bg-zinc-900 p-6 rounded-lg shadow-lg border border-zinc-800">
      {/* Heading with zinc color */}
      <h2 className="text-3xl text-zinc-200 mb-6">
        Jugadores ({players.length}/{maxPlayers})
      </h2>

      <ul className="space-y-3">
        {players.map((player, index) => (
          <li
            key={player.id}
            className="p-4 rounded-lg bg-zinc-800 text-white flex items-center justify-between transition-colors duration-200 hover:bg-zinc-700"
          >
            <span className={`text-lg font-semibold ${getPlayerColor(index)}`}>
              {player.name}
            </span>
            {player.host && (
              <FontAwesomeIcon
                icon={faCrown}
                className="text-yellow-400 text-2xl"
                title="Host"
              />
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
