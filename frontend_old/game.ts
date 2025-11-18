export interface Move {
  player: 1 | -1;
  path: { row: number; col: number; layer: number }[];
  timestamp: number;
}

export type PlayerBlocks = {
  [key: number]: { size4: number; size5: number };
};

export interface GameState {
  board: number[][][];
  currentPlayer: 1 | -1;
  playerBlocks: PlayerBlocks;
  moveHistory: Move[];
}

export interface GameStateForAI {
  board: number[][][];
  currentPlayer: 1 | -1;
  availableBlocks: {
    size4: number;
    size5: number;
  };
  legalMoves: Move[];
}