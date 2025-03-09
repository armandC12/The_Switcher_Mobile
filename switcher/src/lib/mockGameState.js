// src/lib/mockData.js
// src/lib/mockData.js
export const mockPlayers = [
  {
    id: 1,
    name: "Jugador 1",
    turn: "PRIMERO", // Enum de turnos
    game_id: 101,
    game_state_id: 201,
    host: true,
  },
  {
    id: 2,
    name: "Jugador 2",
    turn: "SEGUNDO",
    game_id: 101,
    game_state_id: 201,
    host: false,
  },
  {
    id: 3,
    name: "Jugador 3",
    turn: "TERCERO",
    game_id: 101,
    game_state_id: 201,
    host: false,
  },
  {
    id: 4,
    name: "Jugador 4",
    turn: "CUARTO",
    game_id: 101,
    game_state_id: 201,
    host: false,
  },
];

export const mockMovementCards = [
  {
    id: 1,
    type: "linealContiguo",
    description: "Mueve en línea recta de forma continua",
    used: false,
    player_id: 1,
    game_id: 101,
  },
  {
    id: 2,
    type: "diagonalContiguo",
    description: "Mueve en diagonal, solo a espacios específicos",
    used: false,
    player_id: 1,
    game_id: 101,
  },
  {
    id: 3,
    type: "cruceEnLDerecha",
    description: "Mueve en forma de 'L' hacia la derecha",
    used: false,
    player_id: 1,
    game_id: 101,
  }
];

// Mock de cartas de figura basado en FigureCardSchema
export const mockFigureCards = [
  {
    id: 1,
    type: "analisis",
    show: false,
    difficulty: "EASY", // Ajustar según los valores de DifficultyEnum si los conoces
    player_id: 1,
    game_id: 101,
  },
  {
    id: 2,
    type: "aterrador",
    show: true,
    difficulty: "HARD",
    player_id: 1,
    game_id: 101,
  },
  {
    id: 3,
    type: "analisis",
    show: true,
    difficulty: "EASY",
    player_id: 1,
    game_id: 101,
  },
  {
    id: 4,
    type: "aterrador",
    show: true,
    difficulty: "EASY",
    player_id: 1,
    game_id: 101,
  },
  {
    id: 5,
    type: "analisis",
    show: true,
    difficulty: "EASY",
    player_id: 1,
    game_id: 101,
  },
];
// mock para el tablero de 36 celdas con colores Red, Blue, Green, Yellow
export const mockBoard = [
  // Fila 1
  [
    { color: "Green", posX: 0, posY: 0, game_id: 101, id_box: 1 },
    { color: "Red", posX: 1, posY: 0, game_id: 101, id_box: 2 },
    { color: "Blue", posX: 2, posY: 0, game_id: 101, id_box: 3 },
    { color: "Yellow", posX: 3, posY: 0, game_id: 101, id_box: 4 },
    { color: "Green", posX: 4, posY: 0, game_id: 101, id_box: 5 },
    { color: "Red", posX: 5, posY: 0, game_id: 101, id_box: 6 },
  ],
  // Fila 2
  [
    { color: "Yellow", posX: 0, posY: 1, game_id: 101, id_box: 7 },
    { color: "Blue", posX: 1, posY: 1, game_id: 101, id_box: 8 },
    { color: "Red", posX: 2, posY: 1, game_id: 101, id_box: 9 },
    { color: "Green", posX: 3, posY: 1, game_id: 101, id_box: 10 },
    { color: "Yellow", posX: 4, posY: 1, game_id: 101, id_box: 11 },
    { color: "Blue", posX: 5, posY: 1, game_id: 101, id_box: 12 },
  ],
  // Fila 3
  [
    { color: "Red", posX: 0, posY: 2, game_id: 101, id_box: 13 },
    { color: "Green", posX: 1, posY: 2, game_id: 101, id_box: 14 },
    { color: "Yellow", posX: 2, posY: 2, game_id: 101, id_box: 15 },
    { color: "Blue", posX: 3, posY: 2, game_id: 101, id_box: 16 },
    { color: "Red", posX: 4, posY: 2, game_id: 101, id_box: 17 },
    { color: "Green", posX: 5, posY: 2, game_id: 101, id_box: 18 },
  ],
  // Fila 4
  [
    { color: "Blue", posX: 0, posY: 3, game_id: 101, id_box: 19 },
    { color: "Yellow", posX: 1, posY: 3, game_id: 101, id_box: 20 },
    { color: "Green", posX: 2, posY: 3, game_id: 101, id_box: 21 },
    { color: "Red", posX: 3, posY: 3, game_id: 101, id_box: 22 },
    { color: "Blue", posX: 4, posY: 3, game_id: 101, id_box: 23 },
    { color: "Yellow", posX: 5, posY: 3, game_id: 101, id_box: 24 },
  ],
  // Fila 5
  [
    { color: "Green", posX: 0, posY: 4, game_id: 101, id_box: 25 },
    { color: "Red", posX: 1, posY: 4, game_id: 101, id_box: 26 },
    { color: "Blue", posX: 2, posY: 4, game_id: 101, id_box: 27 },
    { color: "Yellow", posX: 3, posY: 4, game_id: 101, id_box: 28 },
    { color: "Green", posX: 4, posY: 4, game_id: 101, id_box: 29 },
    { color: "Red", posX: 5, posY: 4, game_id: 101, id_box: 30 },
  ],
  // Fila 6
  [
    { color: "Blue", posX: 0, posY: 5, game_id: 101, id_box: 31 },
    { color: "Yellow", posX: 1, posY: 5, game_id: 101, id_box: 32 },
    { color: "Green", posX: 2, posY: 5, game_id: 101, id_box: 33 },
    { color: "Red", posX: 3, posY: 5, game_id: 101, id_box: 34 },
    { color: "Blue", posX: 4, posY: 5, game_id: 101, id_box: 35 },
    { color: "Yellow", posX: 5, posY: 5, game_id: 101, id_box: 36 },
  ],
];


//==========================================
// [{
//   id: 1,
//   type: "linealContiguo",
//   description: "Mueve en línea recta de forma continua",
//   used: false,
//   player_id: 1,
//   game_id: 1,
// },
// {
//   id: 2,
//   type: "diagonalContiguo",
//   description: "Mueve en diagonal, solo a espacios específicos",
//   used: false,
//   player_id: 1,
//   game_id: 1,
// },
// {
//   id: 3,
//   type: "diagonalContiguo",
//   description: "Mueve en forma de 'L' hacia la derecha",
//   used: false,
//   player_id: 1,
//   game_id: 1,
// }]
//==========================================

// export const mockCardsFigure = [
//   { id: 101, type: "aterrador", show: true, difficulty: "EASY" },
//   { id: 105, type: "analisis", show: true, difficulty: "EASY" },
//   { id: 106, type: "aterrador", show: true, difficulty: "EASY" },
//   { id: 102, type: "analisis", show: true, difficulty: "HARD" },
//   { id: 107, type: "analisis", show: true, difficulty: "EASY" },
//   { id: 108, type: "aterrador", show: true, difficulty: "EASY" },
//   { id: 103, type: "analisis", show: true, difficulty: "HARD" },
//   { id: 109, type: "aterrador", show: true, difficulty: "EASY" },
//   { id: 1010, type: "aterrador", show: true, difficulty: "EASY" },
//   { id: 104, type: "analisis", show: true, difficulty: "HARD" }
// ];

// export const mockCardsMovement = [
//   { id: 201, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//   { id: 205, type: "cruceEnLIzquierda", description: "Analiza la situación", used: false },
//   { id: 206, type: "linealContiguo", description: "Analiza la situación", used: false },
//   { id: 202, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//   { id: 207, type: "diagonalContiguo", description: "Analiza la situación", used: false },
//   { id: 208, type: "linealEspaciado", description: "Analiza la situación", used: false },
//   { id: 203, type: "cruceEnLIzquierda", description: "Analiza la situación", used: false },
//   { id: 209, type: "diagonalEspaciado", description: "Analiza la situación", used: false },
//   { id: 210, type: "linealEspaciado", description: "Analiza la situación", used: false },
//   { id: 204, type: "cruceEnLDerecha", description: "Analiza la situación", used: false }
// ];


// export const mockGameState = {
//   id: 1,
//   state: "PLAYING",
//   current_player: 2,
//   players: [
//     {
//       id: 1,
//       name: "Jugador 1",
//       turn: false,
//       figure_cards: [
//         { id: 101, type: "aterrador", show: true, difficulty: "EASY"},
//         { id: 105, type: "analisis", show: true, difficulty: "EASY"},
//         { id: 106, type: "aterrador", show: true, difficulty: "EASY"}
//       ],
//       movement_cards: [
//         { id: 201, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//         { id: 205, type: "cruceEnLIzquierda", description: "Analiza la situación", used: false },
//         { id: 206, type: "linealContiguo", description: "Analiza la situación", used: false }
//       ]
//     },
//     {
//       id: 2,
//       name: "Jugador 2",
//       turn: true,
//       figure_cards: [
//         { id: 102,type: "analisis", show: true, difficulty: "HARD" },
//         { id: 107, type: "analisis", show: true, difficulty: "EASY"},
//         { id: 108, type: "aterrador", show: true, difficulty: "EASY"}
//       ],
//       movement_cards: [
//         { id: 202, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//         { id: 207, type: "diagonalContiguo", description: "Analiza la situación", used: false },
//         { id: 208, type: "linealEspaciado", description: "Analiza la situación", used: false }
//       ]
//     },
//     {
//       id: 3,
//       name: "Jugador 3",
//       turn: false,
//       figure_cards: [
//         { id: 103,type: "analisis", show: true, difficulty: "HARD" },
//         { id: 109, type: "aterrador", show: true, difficulty: "EASY"},
//         { id: 1010, type: "aterrador", show: true, difficulty: "EASY"}
//       ],
//       movement_cards: [
//         { id: 203, type: "cruceEnLIzquierda", description: "Analiza la situación", used: false },
//         { id: 209, type: "diagonalEspaciado", description: "Analiza la situación", used: false },
//         { id: 210, type: "linealEspaciado", description: "Analiza la situación", used: false }
//       ]
//     },
//     {
//       id: 4,
//       name: "Jugador 4",
//       turn: false,
//       figure_cards: [
//         { id: 104,type: "analisis", show: true, difficulty: "HARD" },
//         { id: 107, type: "analisis", show: true, difficulty: "EASY"},
//         { id: 108, type: "aterrador", show: true, difficulty: "EASY"}
//       ],
//       movement_cards: [
//         { id: 204, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//         { id: 209, type: "diagonalContiguo", description: "Analiza la situación", used: false },
//         { id: 210, type: "linealEspaciado", description: "Analiza la situación", used: false }
//       ]
//     }
//   ]
// };

// export const mockPlayers = [
//   {
//     id: 1,
//     name: "Jugador 1",
//     turn: true,
//     figure_cards: [
//       { id: 101, type: "aterrador", show: true, difficulty: "EASY" },
//       { id: 105, type: "analisis", show: true, difficulty: "EASY" },
//       { id: 106, type: "aterrador", show: true, difficulty: "EASY" }
//     ],
//     movement_cards: [
//       { id: 201, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//       { id: 205, type: "cruceEnLIzquierda", description: "Analiza la situación", used: false },
//       { id: 206, type: "linealContiguo", description: "Analiza la situación", used: false }
//     ]
//   },
//   {
//     id: 2,
//     name: "Jugador 2",
//     turn: false,
//     figure_cards: [
//       { id: 102, type: "analisis", show: true, difficulty: "HARD" },
//       { id: 107, type: "analisis", show: true, difficulty: "EASY" },
//       { id: 108, type: "aterrador", show: true, difficulty: "EASY" }
//     ],
//     movement_cards: [
//       { id: 202, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//       { id: 207, type: "diagonalContiguo", description: "Analiza la situación", used: false },
//       { id: 208, type: "linealEspaciado", description: "Analiza la situación", used: false }
//     ]
//   },
//   {
//     id: 3,
//     name: "Jugador 3",
//     turn: false,
//     figure_cards: [
//       { id: 103, type: "analisis", show: true, difficulty: "HARD" },
//       { id: 109, type: "aterrador", show: true, difficulty: "EASY" },
//       { id: 1010, type: "aterrador", show: true, difficulty: "EASY" }
//     ],
//     movement_cards: [
//       { id: 203, type: "cruceEnLIzquierda", description: "Analiza la situación", used: false },
//       { id: 209, type: "diagonalEspaciado", description: "Analiza la situación", used: false },
//       { id: 210, type: "linealEspaciado", description: "Analiza la situación", used: false }
//     ]
//   },
//   {
//     id: 4,
//     name: "Jugador 4",
//     turn: false,
//     figure_cards: [
//       { id: 104, type: "analisis", show: true, difficulty: "HARD" },
//       { id: 107, type: "analisis", show: true, difficulty: "EASY" },
//       { id: 108, type: "aterrador", show: true, difficulty: "EASY" }
//     ],
//     movement_cards: [
//       { id: 204, type: "cruceEnLDerecha", description: "Analiza la situación", used: false },
//       { id: 209, type: "diagonalContiguo", description: "Analiza la situación", used: false },
//       { id: 210, type: "linealEspaciado", description: "Analiza la situación", used: false }
//     ]
//   }
// ];
