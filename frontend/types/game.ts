/**
 * ゲーム関連の型定義
 */

export interface Position {
  row: number;
  col: number;
  layer: number;
}

export interface Move {
  player: 1 | -1;
  path: Position[];
  timestamp?: number;
}

export interface PlayerBlocks {
  size4: number;
  size5: number;
}

export interface GameState {
  board: number[][][];
  currentPlayer: 1 | -1;
  playerBlocks: {
    1: PlayerBlocks;
    [-1]: PlayerBlocks;
  };
  moveHistory: Move[];
  winner?: 1 | -1 | 0 | null;
}

export type GameMode = 'pvp' | 'vsRandom' | 'vsAPI';

