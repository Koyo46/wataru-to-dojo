"""
ゲームロジックモジュール

ワタルートゲームの全体的なロジックを管理するクラスを提供します。
"""

from typing import List, Dict, Literal, Optional, Tuple
import json
from datetime import datetime

from .board import Board
from .move import Move, Position, MoveValidator


class PlayerBlocks:
    """プレイヤーのブロック在庫を管理するクラス"""
    
    def __init__(self, size4: int = 1, size5: int = 1):
        """
        初期化
        
        Args:
            size4: 4マスブロックの数
            size5: 5マスブロックの数
        """
        self.size4 = size4
        self.size5 = size5
    
    def has_block(self, size: int) -> bool:
        """指定サイズのブロックがあるか"""
        if size == 3:
            return True  # 3マスは無限
        elif size == 4:
            return self.size4 > 0
        elif size == 5:
            return self.size5 > 0
        return False
    
    def use_block(self, size: int) -> bool:
        """
        ブロックを使用
        
        Returns:
            使用できた場合True
        """
        if size == 3:
            return True  # 3マスは無限
        elif size == 4:
            if self.size4 > 0:
                self.size4 -= 1
                return True
        elif size == 5:
            if self.size5 > 0:
                self.size5 -= 1
                return True
        return False
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "size4": self.size4,
            "size5": self.size5
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PlayerBlocks":
        """辞書から生成"""
        return cls(size4=data["size4"], size5=data["size5"])
    
    def clone(self) -> "PlayerBlocks":
        """コピーを作成"""
        return PlayerBlocks(self.size4, self.size5)


class WataruToGame:
    """ワタルートゲームのメインクラス"""
    
    def __init__(self, board_size: int = 18, initial_state: Optional[Dict] = None):
        """
        ゲームを初期化
        
        Args:
            board_size: 盤面のサイズ
            initial_state: 初期状態（復元用）
        """
        if initial_state:
            self._load_state(initial_state)
        else:
            self.board = Board(board_size)
            self.current_player: Literal[1, -1] = 1
            self.player_blocks = {
                1: PlayerBlocks(size4=1, size5=1),
                -1: PlayerBlocks(size4=1, size5=1)
            }
            self.move_history: List[Move] = []
            self.winner: Optional[Literal[1, -1, 0]] = None
            
            # 合法手キャッシュ
            self._legal_moves_cache: Optional[List[Move]] = None
            self._cache_valid = False
    
    def _load_state(self, state: Dict) -> None:
        """状態を読み込む"""
        self.board = Board.from_dict(state["board"])
        self.current_player = state["current_player"]
        self.player_blocks = {
            1: PlayerBlocks.from_dict(state["player_blocks"]["1"]),
            -1: PlayerBlocks.from_dict(state["player_blocks"]["-1"])
        }
        self.move_history = [Move.from_dict(m) for m in state["move_history"]]
        self.winner = state.get("winner")
        
        # 合法手キャッシュの初期化
        self._legal_moves_cache: Optional[List[Move]] = None
        self._cache_valid = False
    
    def get_state(self) -> Dict:
        """現在の状態を取得"""
        return {
            "board": self.board.to_dict(),
            "current_player": self.current_player,
            "player_blocks": {
                "1": self.player_blocks[1].to_dict(),
                "-1": self.player_blocks[-1].to_dict()
            },
            "move_history": [m.to_dict() for m in self.move_history],
            "winner": self.winner
        }
    
    def get_state_for_ai(self) -> Dict:
        """Alpha Zero用の状態を取得"""
        return {
            "board": self.board.to_dict()["board"],
            "current_player": self.current_player,
            "available_blocks": self.player_blocks[self.current_player].to_dict(),
            "legal_moves": [m.to_dict() for m in self.get_legal_moves()]
        }
    
    def get_board_as_tensor(self) -> List[List[List[int]]]:
        """盤面をテンソル形式で取得（Alpha Zero用）"""
        return self.board.to_tensor()
    
    def get_legal_moves(self) -> List[Move]:
        """
        現在のプレイヤーの合法手をすべて取得（キャッシング対応）
        
        Returns:
            合法手のリスト
        """
        # キャッシュが有効ならそれを返す
        if self._cache_valid and self._legal_moves_cache is not None:
            return self._legal_moves_cache
        
        if self.winner is not None:
            return []  # ゲーム終了後は手なし
        
        moves: List[Move] = []
        player = self.current_player
        size = self.board.size
        timestamp = datetime.now().timestamp()  # 1回だけ生成して使い回す
        
        # 各マスを起点として探索
        for row in range(size):
            for col in range(size):
                layer1, layer2 = self.board.get_cell(row, col)
                
                # レイヤー2が埋まっている場合はスキップ
                if layer2 != 0:
                    continue
                
                # 起点として配置可能かチェック
                start_layers = []
                if layer1 == 0:
                    start_layers.append(0)  # レイヤー1に配置
                if layer1 == player:
                    start_layers.append(1)  # レイヤー2に配置（橋モード）
                
                if not start_layers:
                    continue
                
                # 各レイヤーで探索
                for start_layer in start_layers:
                    # 2方向に探索（正方向のみ、逆方向は重複なので除外）
                    directions = [(0, 1), (1, 0)]  # 右、下のみ
                    
                    for dr, dc in directions:
                        # 3マス、4マス、5マスの手を生成
                        path = [Position(row, col, start_layer)]
                        current_row, current_col = row, col
                        
                        # 最大5マスまで探索
                        for length in range(1, 5):
                            current_row += dr
                            current_col += dc
                            
                            # 盤面外チェック
                            if not self.board.is_valid_position(current_row, current_col):
                                break
                            
                            next_layer1, next_layer2 = self.board.get_cell(current_row, current_col)
                            
                            # レイヤー2が埋まっている場合は配置不可
                            if next_layer2 != 0:
                                break
                            
                            # 配置可能なレイヤーを決定
                            target_layer = -1
                            if start_layer == 0:
                                # レイヤー1モード
                                if next_layer1 == 0:
                                    target_layer = 0
                                else:
                                    break  # 配置不可
                            else:
                                # レイヤー2モード（橋渡し）
                                if next_layer1 == player or next_layer1 == 0:
                                    target_layer = 1
                                else:
                                    break  # 相手の色がある場合は配置不可
                            
                            path.append(Position(current_row, current_col, target_layer))
                            
                            # 3マス以上で合法手として追加
                            if len(path) >= 3:
                                # 橋モードの場合、終点チェック
                                if start_layer == 1:
                                    end_layer1, _ = self.board.get_cell(current_row, current_col)
                                    if end_layer1 != player:
                                        continue  # 終点が既存マスでない場合はスキップ
                                
                                # ブロック数チェック
                                block_size = len(path)
                                if not self.player_blocks[player].has_block(block_size):
                                    continue
                                
                                # 手を追加
                                try:
                                    move = Move(
                                        player=player,
                                        path=path[:],  # シャローコピーで十分
                                        timestamp=timestamp  # 使い回し
                                    )
                                    moves.append(move)
                                except ValueError:
                                    # 無効な手はスキップ
                                    continue
        
        # キャッシュに保存
        self._legal_moves_cache = moves
        self._cache_valid = True
        
        return moves
    
    def is_valid_move(self, move: Move) -> Tuple[bool, str]:
        """
        手が有効かどうかを検証
        
        Returns:
            (is_valid, error_message)
        """
        # ゲーム終了チェック
        if self.winner is not None:
            return False, "Game is already over"
        
        # プレイヤーチェック
        if move.player != self.current_player:
            return False, f"Not player {move.player}'s turn"
        
        # MoveValidatorを使用して検証
        player_blocks_dict = {
            1: self.player_blocks[1].to_dict(),
            -1: self.player_blocks[-1].to_dict()
        }
        
        return MoveValidator.is_valid_move(
            move, 
            self.board.board, 
            player_blocks_dict
        )
    
    def apply_move(self, move: Move) -> bool:
        """
        手を適用
        
        Args:
            move: 適用する手
            
        Returns:
            成功した場合True
        """
        # 手の妥当性チェック
        is_valid, error_msg = self.is_valid_move(move)
        if not is_valid:
            print(f"Invalid move: {error_msg}")
            return False
        
        # ブロックを使用
        if not self.player_blocks[move.player].use_block(move.block_size):
            print(f"No blocks available for size {move.block_size}")
            return False
        
        # 盤面に手を適用
        for pos in move.path:
            self.board.set_cell(pos.row, pos.col, pos.layer, move.player)
        
        # 履歴に追加
        self.move_history.append(move)
        
        # 勝敗判定
        if self.board.check_bridge(move.player):
            self.winner = move.player
        
        # ターン交代
        if self.winner is None:
            self.current_player = -self.current_player  # type: ignore
        
        # キャッシュを無効化（盤面が変わったので）
        self._cache_valid = False
        
        return True
    
    def check_winner(self) -> Optional[Literal[1, -1, 0]]:
        """
        勝者を判定
        
        Returns:
            1: 水色の勝ち, -1: ピンクの勝ち, 0: 引き分け, None: ゲーム続行中
        """
        if self.winner is not None:
            return self.winner
        
        # 橋の完成チェック
        if self.board.check_bridge(1):
            return 1
        if self.board.check_bridge(-1):
            return -1
        
        # 合法手がない場合は引き分け（まれなケース）
        if len(self.get_legal_moves()) == 0:
            return 0
        
        return None
    
    def is_game_over(self) -> bool:
        """ゲームが終了しているか"""
        return self.winner is not None
    
    def clone(self) -> "WataruToGame":
        """ゲーム状態のコピーを作成"""
        return WataruToGame(
            board_size=self.board.size,
            initial_state=self.get_state()
        )
    
    def reset(self) -> None:
        """ゲームをリセット"""
        self.board.reset()
        self.current_player = 1
        self.player_blocks = {
            1: PlayerBlocks(size4=1, size5=1),
            -1: PlayerBlocks(size4=1, size5=1)
        }
        self.move_history = []
        self.winner = None
        
        # キャッシュを無効化
        self._cache_valid = False
    
    def export_game_record(self) -> str:
        """
        棋譜をJSON形式で出力（学習データ保存用）
        
        Returns:
            JSON文字列
        """
        record = {
            "board_size": self.board.size,
            "moves": [m.to_dict() for m in self.move_history],
            "winner": self.winner,
            "final_state": self.get_state()
        }
        return json.dumps(record, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_game_record(cls, record_json: str) -> "WataruToGame":
        """
        棋譜からゲームを復元
        
        Args:
            record_json: JSON形式の棋譜
            
        Returns:
            復元されたゲーム
        """
        record = json.loads(record_json)
        game = cls(board_size=record["board_size"])
        
        # 手を順番に適用
        for move_dict in record["moves"]:
            move = Move.from_dict(move_dict)
            game.apply_move(move)
        
        return game
    
    def get_game_info(self) -> Dict:
        """
        ゲーム情報を取得
        
        Returns:
            ゲーム情報の辞書
        """
        return {
            "current_player": self.current_player,
            "move_count": len(self.move_history),
            "player_blocks": {
                "1": self.player_blocks[1].to_dict(),
                "-1": self.player_blocks[-1].to_dict()
            },
            "winner": self.winner,
            "is_game_over": self.is_game_over(),
            "legal_moves_count": len(self.get_legal_moves()),
            "board_size": self.board.size
        }
    
    def undo_last_move(self) -> bool:
        """
        最後の手を取り消す
        
        Returns:
            成功した場合True
        """
        if len(self.move_history) == 0:
            return False
        
        # 最後の手を取得
        last_move = self.move_history.pop()
        
        # 盤面から削除
        for pos in last_move.path:
            self.board.set_cell(pos.row, pos.col, pos.layer, 0)
        
        # ブロックを戻す
        if last_move.block_size == 4:
            self.player_blocks[last_move.player].size4 += 1
        elif last_move.block_size == 5:
            self.player_blocks[last_move.player].size5 += 1
        
        # ターンを戻す
        self.current_player = last_move.player
        self.winner = None
        
        return True
    
    def __str__(self) -> str:
        """文字列表現"""
        player_name = "水色" if self.current_player == 1 else "ピンク"
        return (
            f"WataruToGame(\n"
            f"  current_player={player_name},\n"
            f"  moves={len(self.move_history)},\n"
            f"  winner={self.winner},\n"
            f"  board_size={self.board.size}\n"
            f")"
        )
    
    def __repr__(self) -> str:
        return self.__str__()

