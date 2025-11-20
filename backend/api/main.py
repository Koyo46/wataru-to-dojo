"""
FastAPI メインエントリーポイント

ワタルート道場のバックエンドAPIを提供します。
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
import uuid
from datetime import datetime

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from game.game import WataruToGame
from game.move import Move, Position
from game.board import Board
from ai.mcts import create_mcts_engine

# Alpha Zero AI (遅延インポート - 初回使用時にロード)
_alpha_zero_player = None

def get_alpha_zero_player():
    """Alpha Zero AIプレイヤーのシングルトン取得"""
    global _alpha_zero_player
    if _alpha_zero_player is None:
        try:
            from alpha_zero.AlphaZeroPlayer import AlphaZeroPlayer
            _alpha_zero_player = AlphaZeroPlayer(
                model_path='alpha_zero/models/best.pth.tar',
                num_mcts_sims=50,  # 実用的な速度
                board_size=9
            )
        except Exception as e:
            print(f"⚠️ Alpha Zero AI読み込み失敗: {e}")
            _alpha_zero_player = None
    return _alpha_zero_player


# FastAPIアプリケーション
app = FastAPI(
    title="ワタルート道場 API",
    description="ワタルートゲームのバックエンドAPI",
    version="1.0.0"
)

# CORS設定（フロントエンドからのアクセスを許可）
import os

# 環境変数から許可するオリジンを取得
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + ["*"],  # 開発用に全許可（本番では制限推奨）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ゲームセッションを保存する辞書（本番環境ではRedisなどを使用）
game_sessions: Dict[str, WataruToGame] = {}


# === Pydantic Models ===

class PositionModel(BaseModel):
    """位置を表すモデル"""
    row: int = Field(..., ge=0, lt=18)
    col: int = Field(..., ge=0, lt=18)
    layer: int = Field(..., ge=0, le=1)


class MoveModel(BaseModel):
    """手を表すモデル"""
    player: Literal[1, -1]
    path: List[PositionModel]
    timestamp: Optional[float] = None


class NewGameRequest(BaseModel):
    """新規ゲーム作成リクエスト"""
    board_size: int = Field(default=18, ge=3, le=30)


class NewGameResponse(BaseModel):
    """新規ゲーム作成レスポンス"""
    game_id: str
    state: Dict


class ApplyMoveRequest(BaseModel):
    """手を適用するリクエスト"""
    game_id: str
    move: MoveModel


class ApplyMoveResponse(BaseModel):
    """手を適用するレスポンス"""
    success: bool
    state: Dict
    winner: Optional[Literal[1, -1, 0]] = None
    message: Optional[str] = None


class GameStateResponse(BaseModel):
    """ゲーム状態レスポンス"""
    game_id: str
    state: Dict
    info: Dict


class LegalMovesResponse(BaseModel):
    """合法手リストレスポンス"""
    game_id: str
    legal_moves: List[Dict]
    count: int


class AIMovesRequest(BaseModel):
    """AI手取得リクエスト"""
    game_id: str
    player: Literal[1, -1]
    difficulty: Literal["easy", "hard"] = "hard"  # easy=Pure MCTS, hard=Tactical MCTS


class AIMovesResponse(BaseModel):
    """AI手取得レスポンス"""
    game_id: str
    move: Optional[Dict]
    message: str


# === API エンドポイント ===

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "ワタルート道場 API",
        "version": "1.0.0",
        "endpoints": {
            "new_game": "POST /api/game/new",
            "get_state": "GET /api/game/{game_id}/state",
            "apply_move": "POST /api/game/move",
            "legal_moves": "GET /api/game/{game_id}/legal-moves",
            "ai_move": "POST /api/ai/move",
            "reset": "POST /api/game/{game_id}/reset",
            "undo": "POST /api/game/{game_id}/undo"
        }
    }


@app.post("/api/game/new", response_model=NewGameResponse)
async def create_new_game(request: NewGameRequest):
    """
    新しいゲームを作成
    
    Args:
        request: 新規ゲーム作成リクエスト
        
    Returns:
        ゲームIDと初期状態
    """
    game_id = str(uuid.uuid4())
    game = WataruToGame(board_size=request.board_size)
    game_sessions[game_id] = game
    
    return NewGameResponse(
        game_id=game_id,
        state=game.get_state()
    )


@app.get("/api/game/{game_id}/state", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    """
    ゲーム状態を取得
    
    Args:
        game_id: ゲームID
        
    Returns:
        現在のゲーム状態
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[game_id]
    
    return GameStateResponse(
        game_id=game_id,
        state=game.get_state(),
        info=game.get_game_info()
    )


@app.post("/api/game/move", response_model=ApplyMoveResponse)
async def apply_move(request: ApplyMoveRequest):
    """
    手を適用
    
    Args:
        request: 手を適用するリクエスト
        
    Returns:
        適用結果と新しい状態
    """
    if request.game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[request.game_id]
    
    # MoveModelをMoveオブジェクトに変換
    try:
        positions = [
            Position(row=pos.row, col=pos.col, layer=pos.layer)
            for pos in request.move.path
        ]
        
        timestamp = request.move.timestamp or datetime.now().timestamp()
        
        move = Move(
            player=request.move.player,
            path=positions,
            timestamp=timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid move format: {str(e)}")
    
    # 手を適用
    success = game.apply_move(move)
    
    if not success:
        is_valid, error_msg = game.is_valid_move(move)
        return ApplyMoveResponse(
            success=False,
            state=game.get_state(),
            message=f"Failed to apply move: {error_msg}"
        )
    
    # 勝者チェック
    winner = game.check_winner()
    
    return ApplyMoveResponse(
        success=True,
        state=game.get_state(),
        winner=winner,
        message="Move applied successfully"
    )


@app.get("/api/game/{game_id}/legal-moves", response_model=LegalMovesResponse)
async def get_legal_moves(game_id: str):
    """
    合法手のリストを取得
    
    Args:
        game_id: ゲームID
        
    Returns:
        合法手のリスト
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[game_id]
    legal_moves = game.get_legal_moves()
    
    return LegalMovesResponse(
        game_id=game_id,
        legal_moves=[move.to_dict() for move in legal_moves],
        count=len(legal_moves)
    )


@app.post("/api/ai/move", response_model=AIMovesResponse)
async def get_ai_move(request: AIMovesRequest):
    """
    MCTS AIの手を取得
    
    Args:
        request: AI手取得リクエスト
        
    Returns:
        AIが選択した手
    """
    if request.game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[request.game_id]
    
    # 現在のプレイヤーチェック
    if game.current_player != request.player:
        raise HTTPException(
            status_code=400, 
            detail=f"Not player {request.player}'s turn"
        )
    
    # ゲーム終了チェック
    if game.winner is not None:
        raise HTTPException(status_code=400, detail="Game is already finished")
    
    # 難易度に応じてMCTSエンジンを作成
    use_tactical = request.difficulty == "hard"
    ai_mode = "Tactical MCTS" if use_tactical else "Pure MCTS"
    
    print(f"[MCTS AI] 思考開始（プレイヤー: {request.player}, モード: {ai_mode}）")
    
    mcts = create_mcts_engine(
        time_limit=10.0,  # 10秒で探索
        exploration_weight=1.41,
        verbose=True,  # サーバーログに統計情報を出力
        use_tactical_heuristics=use_tactical
    )
    
    # 最良の手を探索
    best_move = mcts.search(game)
    
    if best_move is None:
        return AIMovesResponse(
            game_id=request.game_id,
            move=None,
            message="No legal moves available"
        )
    
    print(f"[MCTS AI] 選択完了: {best_move}")
    
    # メッセージに難易度を含める
    difficulty_label = "難易度: 難しい" if use_tactical else "難易度: 簡単"
    
    return AIMovesResponse(
        game_id=request.game_id,
        move=best_move.to_dict(),
        message=f"{ai_mode} ({difficulty_label}, 勝率: {mcts.stats.best_move_win_rate*100:.1f}%)"
    )


@app.post("/api/ai/alpha-zero-move", response_model=AIMovesResponse)
async def get_alpha_zero_move(request: AIMovesRequest):
    """
    Alpha Zero AIの手を取得
    
    Args:
        request: AI手取得リクエスト
        
    Returns:
        Alpha Zero AIが選択した手
    """
    if request.game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[request.game_id]
    
    # 現在のプレイヤーチェック
    if game.current_player != request.player:
        raise HTTPException(
            status_code=400, 
            detail=f"Not player {request.player}'s turn"
        )
    
    # ゲーム終了チェック
    if game.winner is not None:
        raise HTTPException(status_code=400, detail="Game is already finished")
    
    # Alpha Zero AIプレイヤーを取得
    alpha_zero_ai = get_alpha_zero_player()
    
    if alpha_zero_ai is None:
        raise HTTPException(
            status_code=503, 
            detail="Alpha Zero AI is not available. Model may not be loaded."
        )
    
    print(f"[Alpha Zero AI] 思考開始（プレイヤー: {request.player}）")
    
    try:
        # Alpha Zero AIで手を取得
        best_move = alpha_zero_ai.get_move(game)
        
        if best_move is None:
            return AIMovesResponse(
                game_id=request.game_id,
                move=None,
                message="No legal moves available"
            )
        
        print(f"[Alpha Zero AI] 選択完了: {best_move}")
        
        return AIMovesResponse(
            game_id=request.game_id,
            move=best_move.to_dict(),
            message="Alpha Zero AI (強化学習モデル)"
        )
    
    except Exception as e:
        print(f"[Alpha Zero AI] エラー: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Alpha Zero AI error: {str(e)}")


@app.post("/api/game/{game_id}/reset")
async def reset_game(game_id: str):
    """
    ゲームをリセット
    
    Args:
        game_id: ゲームID
        
    Returns:
        リセット後の状態
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[game_id]
    game.reset()
    
    return {
        "game_id": game_id,
        "state": game.get_state(),
        "message": "Game reset successfully"
    }


@app.post("/api/game/{game_id}/undo")
async def undo_move(game_id: str):
    """
    最後の手を取り消す
    
    Args:
        game_id: ゲームID
        
    Returns:
        取り消し後の状態
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[game_id]
    success = game.undo_last_move()
    
    if not success:
        raise HTTPException(status_code=400, detail="No moves to undo")
    
    return {
        "game_id": game_id,
        "state": game.get_state(),
        "message": "Move undone successfully"
    }


@app.delete("/api/game/{game_id}")
async def delete_game(game_id: str):
    """
    ゲームセッションを削除
    
    Args:
        game_id: ゲームID
        
    Returns:
        削除結果
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    del game_sessions[game_id]
    
    return {
        "message": "Game deleted successfully",
        "game_id": game_id
    }


@app.get("/api/games")
async def list_games():
    """
    現在のゲームセッション一覧を取得
    
    Returns:
        ゲームセッションのリスト
    """
    games_info = []
    
    for game_id, game in game_sessions.items():
        games_info.append({
            "game_id": game_id,
            "info": game.get_game_info()
        })
    
    return {
        "count": len(games_info),
        "games": games_info
    }


@app.get("/api/game/{game_id}/export")
async def export_game_record(game_id: str):
    """
    棋譜をエクスポート
    
    Args:
        game_id: ゲームID
        
    Returns:
        JSON形式の棋譜
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = game_sessions[game_id]
    record = game.export_game_record()
    
    return {
        "game_id": game_id,
        "record": record
    }


# === ヘルスチェック ===

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_games": len(game_sessions)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

