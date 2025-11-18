"""
手の管理モジュール

ゲーム内の手（Move）を表現するクラスと関連する機能を提供します。
"""

from typing import List, Dict, Literal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Position:
    """盤面上の位置を表すクラス"""
    row: int
    col: int
    layer: int  # 0: レイヤー1, 1: レイヤー2
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "row": self.row,
            "col": self.col,
            "layer": self.layer
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Position":
        """辞書から生成"""
        return cls(
            row=data["row"],
            col=data["col"],
            layer=data["layer"]
        )


@dataclass
class Move:
    """ゲーム内の手を表すクラス"""
    player: Literal[1, -1]  # 1: 水色プレイヤー, -1: ピンクプレイヤー
    path: List[Position]  # 配置するマスのリスト
    timestamp: float  # タイムスタンプ
    
    def __post_init__(self):
        """初期化後の検証"""
        if self.player not in [1, -1]:
            raise ValueError("player must be 1 or -1")
        
        if len(self.path) < 3 or len(self.path) > 5:
            raise ValueError("path length must be between 3 and 5")
    
    @property
    def block_size(self) -> int:
        """ブロックサイズを取得"""
        return len(self.path)
    
    @property
    def is_bridge_mode(self) -> bool:
        """橋渡しモードかどうか"""
        return self.path[0].layer == 1
    
    @property
    def start_position(self) -> Position:
        """開始位置を取得"""
        return self.path[0]
    
    @property
    def end_position(self) -> Position:
        """終了位置を取得"""
        return self.path[-1]
    
    @property
    def direction(self) -> str:
        """方向を取得 (horizontal/vertical)"""
        if len(self.path) < 2:
            return "none"
        
        first = self.path[0]
        second = self.path[1]
        
        if first.row == second.row:
            return "horizontal"
        elif first.col == second.col:
            return "vertical"
        else:
            return "invalid"
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "player": self.player,
            "path": [pos.to_dict() for pos in self.path],
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Move":
        """辞書から生成"""
        return cls(
            player=data["player"],
            path=[Position.from_dict(pos) for pos in data["path"]],
            timestamp=data["timestamp"]
        )
    
    @classmethod
    def create(cls, player: Literal[1, -1], path: List[Dict]) -> "Move":
        """便利なファクトリメソッド"""
        positions = [Position.from_dict(pos) for pos in path]
        return cls(
            player=player,
            path=positions,
            timestamp=datetime.now().timestamp()
        )
    
    def validate_path(self) -> bool:
        """パスの妥当性を検証"""
        if len(self.path) < 3 or len(self.path) > 5:
            return False
        
        # 一直線かどうかチェック
        all_same_row = all(pos.row == self.path[0].row for pos in self.path)
        all_same_col = all(pos.col == self.path[0].col for pos in self.path)
        
        if not (all_same_row or all_same_col):
            return False
        
        # 重複チェック
        positions_set = set((pos.row, pos.col, pos.layer) for pos in self.path)
        if len(positions_set) != len(self.path):
            return False
        
        # ソートして連続性をチェック
        if all_same_row:
            # 横一列の場合、列番号でソート
            sorted_path = sorted(self.path, key=lambda p: p.col)
            for i in range(len(sorted_path) - 1):
                if sorted_path[i + 1].col - sorted_path[i].col != 1:
                    return False
        else:
            # 縦一列の場合、行番号でソート
            sorted_path = sorted(self.path, key=lambda p: p.row)
            for i in range(len(sorted_path) - 1):
                if sorted_path[i + 1].row - sorted_path[i].row != 1:
                    return False
        
        return True
    
    def __str__(self) -> str:
        """文字列表現"""
        player_name = "水色" if self.player == 1 else "ピンク"
        start = self.start_position
        end = self.end_position
        return (
            f"Move({player_name}, "
            f"size={self.block_size}, "
            f"from=({start.row},{start.col}), "
            f"to=({end.row},{end.col}), "
            f"dir={self.direction})"
        )
    
    def __repr__(self) -> str:
        return self.__str__()


class MoveValidator:
    """手の妥当性を検証するクラス"""
    
    @staticmethod
    def is_valid_move(move: Move, board: List[List[List[int]]], 
                      player_blocks: Dict) -> tuple[bool, str]:
        """
        手が有効かどうかを検証
        
        Returns:
            (is_valid, error_message)
        """
        # パスの妥当性チェック
        if not move.validate_path():
            return False, "Invalid path: not straight or not continuous"
        
        # ブロック数チェック
        current_player_blocks = player_blocks.get(move.player, {})
        if move.block_size == 4:
            if current_player_blocks.get("size4", 0) <= 0:
                return False, "No 4-size blocks available"
        elif move.block_size == 5:
            if current_player_blocks.get("size5", 0) <= 0:
                return False, "No 5-size blocks available"
        
        # パスをソート（横一列なら列順、縦一列なら行順）
        all_same_row = all(pos.row == move.path[0].row for pos in move.path)
        if all_same_row:
            sorted_path = sorted(move.path, key=lambda p: p.col)
        else:
            sorted_path = sorted(move.path, key=lambda p: p.row)
        
        # 盤面の状態チェック（ソート済みのパスを使用）
        for i, pos in enumerate(sorted_path):
            if pos.row < 0 or pos.row >= len(board):
                return False, f"Position out of bounds: row={pos.row}"
            if pos.col < 0 or pos.col >= len(board[0]):
                return False, f"Position out of bounds: col={pos.col}"
            
            layer1, layer2 = board[pos.row][pos.col]
            
            # レイヤー2が既に埋まっている場合
            if layer2 != 0:
                return False, f"Layer 2 already occupied at ({pos.row},{pos.col})"
            
            # 起点の場合
            if i == 0:
                if pos.layer == 0:
                    # レイヤー1モード: レイヤー1が空でなければならない
                    if layer1 != 0:
                        return False, f"Layer 1 not empty at start position ({pos.row},{pos.col})"
                elif pos.layer == 1:
                    # レイヤー2モード（橋渡し）: レイヤー1に自分の色がなければならない
                    if layer1 != move.player:
                        return False, f"Layer 1 must have player color at start position ({pos.row},{pos.col})"
            else:
                # 2マス目以降
                first_layer = sorted_path[0].layer
                
                if first_layer == 0:
                    # レイヤー1モード
                    if pos.layer != 0 or layer1 != 0:
                        return False, f"Layer 1 not empty at ({pos.row},{pos.col})"
                else:
                    # レイヤー2モード
                    if pos.layer != 1:
                        return False, f"Must place on layer 2 in bridge mode at ({pos.row},{pos.col})"
                    if layer1 != 0 and layer1 != move.player:
                        return False, f"Cannot place on opponent's color at ({pos.row},{pos.col})"
        
        # 橋渡しモードの場合、終点チェック
        if move.is_bridge_mode:
            end_pos = move.end_position
            end_layer1 = board[end_pos.row][end_pos.col][0]
            if end_layer1 != move.player:
                return False, "Bridge mode: end position must be on existing player tile"
        
        return True, ""

