import { WataruToGame } from './gameLogic';
import { Move } from '../types/game';

export class RandomAI {
  constructor(private player: 1 | -1) {}

  // ランダムな合法手を選択
  selectMove(game: WataruToGame): Move | null {
    const legalMoves = game.getLegalMoves();
    
    if (legalMoves.length === 0) {
      return null;
    }

    // ランダムに1つ選ぶ
    const randomIndex = Math.floor(Math.random() * legalMoves.length);
    return legalMoves[randomIndex];
  }

  // ちょっとだけ賢くする場合（オプション）
  selectMoveWithSimpleHeuristic(game: WataruToGame): Move | null {
    const legalMoves = game.getLegalMoves();
    
    if (legalMoves.length === 0) {
      return null;
    }

    // 例: 5マスブロックを優先的に使う
    const fiveTileMoves = legalMoves.filter(m => m.path.length === 5);
    if (fiveTileMoves.length > 0) {
      const randomIndex = Math.floor(Math.random() * fiveTileMoves.length);
      return fiveTileMoves[randomIndex];
    }

    // 次に4マスブロック
    const fourTileMoves = legalMoves.filter(m => m.path.length === 4);
    if (fourTileMoves.length > 0) {
      const randomIndex = Math.floor(Math.random() * fourTileMoves.length);
      return fourTileMoves[randomIndex];
    }

    // なければランダム
    const randomIndex = Math.floor(Math.random() * legalMoves.length);
    return legalMoves[randomIndex];
  }
}

