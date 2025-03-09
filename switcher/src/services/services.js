const apiUrl = import.meta.env.VITE_API_URL;
// console.log(import.meta.env);

export async function getGames(currentPage, data, isFiltering) {

    if (!isFiltering) {
      const url = `${apiUrl}/games?page=${currentPage}&limit=5`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const data = await response.json();

      return data;
    }
    else{
      const url = new URL(`${apiUrl}/games`);
      url.searchParams.append('page', 1);
      url.searchParams.append('limit', 5);

      const name = data.name;
      const players = data.players;

      if (name) {
        url.searchParams.append('name', name);
      }

      if (players) {
        url.searchParams.append('num_players', players);
      }

      try {
        const response = await fetch(url.toString(), {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) {
          const errorMessage = await response.text();
          throw new Error(`Error al filtrar partidas: ${errorMessage}`);
        }
        return await response.json();
      }
      catch (error) {
        throw new Error(`Error al filtrar partidas: ${error.message}`);
      }
    }
}


// Obtener jugadores
export async function getPlayers(gameId) {
    const url = `${apiUrl}/players/${gameId}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const data = await response.json();

    return data;
}

// Obtener cartas de movimiento para cada jugador
export async function getDeckMovement(gameId, player) {
    // console.log("gameIDMov: ", gameId);
    // console.log("playerMov: ", player);
    const url = `${apiUrl}/deck/movement/${gameId}/${player}`;

    const response = await fetch(url);
    // console.log(response);
    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const data = await response.json();
    // console.log("cardsMOV: ", data);
    return data;
}

// Obtener cartas de figura para cada jugador
export async function getDeckFigure(gameId, player) {
    // console.log("gameIDFig: ", gameId);
    // console.log("playerFig: ", player);
    const url = `${apiUrl}/deck/figure/${gameId}/${player}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const data = await response.json();
    // console.log("cardsFIG: ", data);
    return data;
}


export async function getGameInfo(gameId) {
    const url = `${apiUrl}/games/${gameId}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const data = await response.json();

    return data;
}

export async function getPlayer(gameId, playerId) {
    const url = `${apiUrl}/players/${gameId}/${playerId}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const data = await response.json();

    return data;
}

export async function startGame(gameId) {
    const url = `${apiUrl}/game_state/start/${gameId}`;

    const response = await fetch(url, {
        method: 'PATCH',
        headers: {
        'Content-Type': 'application/json',
        }
    });

    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const data = await response.json();

    return data;
}


export async function joinGame(gameId, playerName, password) {
  const url = `${apiUrl}/players/join/${gameId}`;
  console.log(`Password to send: ${password}`); // Logging the password to confirm it's being passed

  try {
      const payload = {
          player_name: playerName,
          password: password
      };


      console.log(JSON.stringify(payload))
      const response = await fetch(url, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
      });

      if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`Error: ${errorData.detail || `Response status: ${response.status}`}`);
      }

      const data = await response.json();
      return data;
  } catch (error) {
      console.error("Join game failed:", error);
      throw error; 
  }
}

// Finalizar turno
export async function pathEndTurn(gameId) {
    try {
      const response = await fetch(`${apiUrl}/game_state/${gameId}/finish_turn`, {
        method: 'PATCH',  // Método PATCH para actualizar el turno
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Error al finalizar el turno');
      }

      return await response.json(); // Asumiendo que devuelve algún JSON como respuesta
    } catch (error) {
      console.error('Error al llamar al endpoint de finalizar turno:', error);
      throw error; // Propaga el error para manejarlo en el componente
    }
  }

  // Obtener el estado del juego
export async function getGameStatus(gameId) {
    const url = `${apiUrl}/game_status/${gameId}/status`;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Error al obtener el estado del juego: ${response.status}`);
      }

      const data = await response.json();
      return data.state; // Suponiendo que la respuesta contiene { state: "FINISHED" | "PLAYING" | "WAITING" }
    } catch (error) {
      console.error('Error en la llamada a getGameStatus:', error);
      throw error;
    }
  }

  export async function getBoard(gameId) {
    const url = `${apiUrl}/board/${gameId}`;

    try {
      const response = await fetch(url);
      // console.log("BOARD services: ",response);
      if (!response.ok) {
        throw new Error('Error al obtener tablero');
      }

      return await response.json(); // Asumiendo que devuelve algún JSON como respuesta
    } catch (error) {
      console.error('Error al obtener turno:', error);
      throw error; // Propaga el error para manejarlo en el componente
    }
  }

export const fetchTurnInfo = async (activeGameId) => {
    try {
        const response = await fetch(`${apiUrl}/game_state/${activeGameId}/current_turn`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        
        const data = await response.json();

        console.log(data);
        return data;
    } catch (error) {
      throw new Error(`Error al obtener información del turno ${error.message}`);
    }
}

export const playMovementCard = async ({gameId, playerId, cardId, posFrom, posTo}) => {
  try {
    const response = await fetch(`${apiUrl}/deck/movement/play_card`, {
      method: 'POST',
      headers: {
      'Content-Type': 'application/json',
      },
      body: JSON.stringify({
      game_id: gameId,
      player_id: playerId,
      card_id: cardId,
      pos_from: { pos: [posFrom.x, posFrom.y] },
      pos_to: { pos: [posTo.x, posTo.y] },
      }),
    });
    // console.log(response);
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error al jugar la carta: ${errorMessage}`);
    }
    return await response.json();
    // console.log('La Carta fue jugada exitosamente!');
  }   catch (error) {
    throw new Error(`Error al jugar la carta: ${error.message}`);
  }
};

export const undoMovement = async (gameId, playerId) => {
  const url = `${apiUrl}/deck/movement/${gameId}/${playerId}/undo_move`
  try {
      const response = await fetch(url,
          {
              method:`POST`,
              headers: { 'Content-Type': 'application/json' },
          }
      )
      if (!response.ok){
          const errorMessage = await response.text();
          throw new Error(`Error al deshacer movimiento: ${errorMessage}`);
      }
  }
  catch (error) {
    throw new Error(`Error al deshacer movimiento: ${error.message}`);
  }
}

export const submitForm = async (data, username) => {
  const body = {
    game: {
      name: data.name,
      max_players: data.playersRange[1],
      min_players: data.playersRange[0],
      password: data.password
    },
    player: {
      name: username,
      host: true,
      turn: "PRIMERO",
    },
  };

  return await fetch(`${apiUrl}/games`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(errorData => {
          throw new Error(errorData.message || 'Error al crear la partida.');
        });
      }
      return response.json();
    });
}

export const leaveGame = async (playerId, gameId) => {
  try {
    const response = await fetch(`${apiUrl}/players/${playerId}/leave?game_id=${gameId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    // console.log(response)
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error al abandonar la partida: ${errorMessage}`);
    }
    return await response.json()
  }
  catch (error) {
    throw new Error(`Error al abandonar la partida: ${error.message}`);
  }
}

export const claimFigure = async (gameId, playerId, cardId, figure) => {
  const url = `${apiUrl}/deck/figure/play_card`;
  const body = {
    game_id: gameId,
    player_id: playerId,
    card_id: cardId,
    figure: figure
  };
  // console.log(`body sent to claim figure: ${JSON.stringify(body)}`);

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: JSON.stringify(body),
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error al reclamar figura: ${errorMessage}`);
    }
    return response.json();
  }
  catch (error) {
    throw new Error(`Error al reclamar figura: ${error.message}`);
  }
}

export const calculateFigures = async (gameId) => {
  const url = `${apiUrl}/board/calculate_figures/${gameId}`;
  
  try {
    const response = await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error al calcular figuras: ${errorMessage}`);
    }
    return response.json();
  }
  catch (error) {
    throw new Error(`Error al calcular figuras: ${error.message}`);
  }
}

export const blockCardFigure = async (gameId, blockerPlayerId, blockedPlayerId, cardId, figure) => {
  const url = `${apiUrl}/deck/figure/block_card`;
  const body = {
    game_id: gameId,
    blocker_player_id: blockerPlayerId,
    blocked_player_id: blockedPlayerId,
    card_id: cardId,
    figure: figure
  };
  console.log(`body sent to block card: ${JSON.stringify(body)}`);

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: JSON.stringify(body),
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error al bloquear carta: ${errorMessage}`);
    }
    return response.json();
  }
  catch (error) {
    throw new Error(`Error al bloquear carta: ${error.message}`);
  }
}

export const fetchGameState = async (activeGameId) => {
  try {
      const response = await fetch(`${apiUrl}/game_state/${activeGameId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();

      console.log(data);
      return data;
  } catch (error) {
    throw new Error(`Error al obtener información del turno ${error.message}`);
  }
}
