/**
 * バックエンドAPIクライアント
 * 
 * FastAPIバックエンドと通信するためのクライアントライブラリ
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  board: {
    size: number;
    board: number[][][];
  };
  current_player: 1 | -1;
  player_blocks: {
    "1": PlayerBlocks;
    "-1": PlayerBlocks;
  };
  move_history: Move[];
  winner: 1 | -1 | 0 | null;
}

export interface GameInfo {
  current_player: 1 | -1;
  move_count: number;
  player_blocks: {
    "1": PlayerBlocks;
    "-1": PlayerBlocks;
  };
  winner: 1 | -1 | 0 | null;
  is_game_over: boolean;
  legal_moves_count: number;
  board_size: number;
}

export interface NewGameResponse {
  game_id: string;
  state: GameState;
}

export interface GameStateResponse {
  game_id: string;
  state: GameState;
  info: GameInfo;
}

export interface ApplyMoveResponse {
  success: boolean;
  state: GameState;
  winner?: 1 | -1 | 0 | null;
  message?: string;
}

export interface LegalMovesResponse {
  game_id: string;
  legal_moves: Move[];
  count: number;
}

export interface AIMovesResponse {
  game_id: string;
  move: Move | null;
  message: string;
}

/**
 * APIクライアントクラス
 */
export class WataruToAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * 新しいゲームを作成
   */
  async createNewGame(boardSize: number = 18): Promise<NewGameResponse> {
    const response = await fetch(`${this.baseUrl}/api/game/new`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ board_size: boardSize }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create new game: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * ゲーム状態を取得
   */
  async getGameState(gameId: string): Promise<GameStateResponse> {
    const response = await fetch(`${this.baseUrl}/api/game/${gameId}/state`);

    if (!response.ok) {
      throw new Error(`Failed to get game state: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 手を適用
   */
  async applyMove(gameId: string, move: Move): Promise<ApplyMoveResponse> {
    const response = await fetch(`${this.baseUrl}/api/game/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        game_id: gameId,
        move: move,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to apply move: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 合法手のリストを取得
   */
  async getLegalMoves(gameId: string): Promise<LegalMovesResponse> {
    const response = await fetch(`${this.baseUrl}/api/game/${gameId}/legal-moves`);

    if (!response.ok) {
      throw new Error(`Failed to get legal moves: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * AIの手を取得
   */
  async getAIMove(gameId: string, player: 1 | -1, difficulty: 'easy' | 'hard' = 'hard'): Promise<AIMovesResponse> {
    const response = await fetch(`${this.baseUrl}/api/ai/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        game_id: gameId,
        player: player,
        difficulty: difficulty,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get AI move: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * ゲームをリセット
   */
  async resetGame(gameId: string): Promise<GameStateResponse> {
    const response = await fetch(`${this.baseUrl}/api/game/${gameId}/reset`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to reset game: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 最後の手を取り消す
   */
  async undoMove(gameId: string): Promise<GameStateResponse> {
    const response = await fetch(`${this.baseUrl}/api/game/${gameId}/undo`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to undo move: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * ゲームセッションを削除
   */
  async deleteGame(gameId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/game/${gameId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete game: ${response.statusText}`);
    }
  }

  /**
   * ヘルスチェック
   */
  async healthCheck(): Promise<{ status: string; timestamp: string; active_games: number }> {
    const response = await fetch(`${this.baseUrl}/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// デフォルトのクライアントインスタンスをエクスポート
export const apiClient = new WataruToAPIClient();

