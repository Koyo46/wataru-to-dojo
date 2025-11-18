"""
盤面管理モジュール

ゲームの盤面状態を管理するクラスを提供します。
"""

from typing import List, Tuple, Literal, Optional
import copy


class Board:
    """ゲーム盤面を管理するクラス"""
    
    def __init__(self, size: int = 18):
        """
        盤面を初期化
        
        Args:
            size: 盤面のサイズ（デフォルト: 18x18）
        """
        self.size = size
        # board[row][col] = [layer1, layer2]
        # 0: 空, 1: 水色, -1: ピンク
        self.board: List[List[List[int]]] = [
            [[0, 0] for _ in range(size)] for _ in range(size)
        ]
    
    def get_cell(self, row: int, col: int) -> Tuple[int, int]:
        """
        指定したセルの状態を取得
        
        Args:
            row: 行
            col: 列
            
        Returns:
            (layer1, layer2) のタプル
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        
        return tuple(self.board[row][col])
    
    def set_cell(self, row: int, col: int, layer: int, value: Literal[0, 1, -1]) -> None:
        """
        指定したセルに値を設定
        
        Args:
            row: 行
            col: 列
            layer: レイヤー（0 or 1）
            value: 設定する値（0: 空, 1: 水色, -1: ピンク）
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        
        if layer not in [0, 1]:
            raise ValueError(f"Invalid layer: {layer}")
        
        if value not in [0, 1, -1]:
            raise ValueError(f"Invalid value: {value}")
        
        self.board[row][col][layer] = value
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """位置が盤面内かどうかをチェック"""
        return 0 <= row < self.size and 0 <= col < self.size
    
    def is_empty(self, row: int, col: int, layer: int) -> bool:
        """指定したセルのレイヤーが空かどうか"""
        if not self.is_valid_position(row, col):
            return False
        
        return self.board[row][col][layer] == 0
    
    def has_player_color(self, row: int, col: int, player: Literal[1, -1]) -> bool:
        """
        指定したセルにプレイヤーの色があるか（レイヤー1またはレイヤー2）
        
        Args:
            row: 行
            col: 列
            player: プレイヤー（1 or -1）
            
        Returns:
            プレイヤーの色がある場合True
        """
        if not self.is_valid_position(row, col):
            return False
        
        layer1, layer2 = self.board[row][col]
        return layer1 == player or layer2 == player
    
    def can_place_on_layer1(self, row: int, col: int) -> bool:
        """レイヤー1に配置可能かチェック"""
        if not self.is_valid_position(row, col):
            return False
        
        layer1, layer2 = self.board[row][col]
        return layer1 == 0 and layer2 == 0
    
    def can_place_on_layer2(self, row: int, col: int, player: Literal[1, -1]) -> bool:
        """
        レイヤー2に配置可能かチェック
        
        Args:
            row: 行
            col: 列
            player: プレイヤー（1 or -1）
            
        Returns:
            配置可能な場合True
        """
        if not self.is_valid_position(row, col):
            return False
        
        layer1, layer2 = self.board[row][col]
        
        # レイヤー2が既に埋まっている場合は不可
        if layer2 != 0:
            return False
        
        # レイヤー1が空、または自分の色の場合は可能
        return layer1 == 0 or layer1 == player
    
    def check_bridge(self, player: Literal[1, -1]) -> bool:
        """
        プレイヤーが橋を完成させたかチェック（勝利判定）
        
        Args:
            player: プレイヤー（1: 水色は上下、-1: ピンクは左右）
            
        Returns:
            橋が完成している場合True
        """
        visited = [[False] * self.size for _ in range(self.size)]
        stack = []
        
        # スタート地点を探す
        if player == 1:
            # 水色は上の端（row=0）からスタート
            for col in range(self.size):
                if self.has_player_color(0, col, player):
                    stack.append((0, col))
                    visited[0][col] = True
        else:
            # ピンクは左の端（col=0）からスタート
            for row in range(self.size):
                if self.has_player_color(row, 0, player):
                    stack.append((row, 0))
                    visited[row][0] = True
        
        # 深さ優先探索で反対側まで到達できるかチェック
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # 下、上、右、左
        
        while stack:
            row, col = stack.pop()
            
            # ゴール判定
            if player == 1 and row == self.size - 1:
                return True  # 水色: 下端に到達
            if player == -1 and col == self.size - 1:
                return True  # ピンク: 右端に到達
            
            # 4方向を探索
            for dr, dc in directions:
                nr, nc = row + dr, col + dc
                
                if (self.is_valid_position(nr, nc) and 
                    not visited[nr][nc] and 
                    self.has_player_color(nr, nc, player)):
                    
                    visited[nr][nc] = True
                    stack.append((nr, nc))
        
        return False
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        指定したセルの隣接セル（上下左右）を取得
        
        Args:
            row: 行
            col: 列
            
        Returns:
            隣接セルのリスト [(row, col), ...]
        """
        neighbors = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if self.is_valid_position(nr, nc):
                neighbors.append((nr, nc))
        
        return neighbors
    
    def to_tensor(self) -> List[List[List[int]]]:
        """
        盤面をテンソル形式に変換（Alpha Zero用）
        
        Returns:
            [channel, row, col] 形式の3次元リスト
            channel 0: player 1 layer 1
            channel 1: player 1 layer 2
            channel 2: player -1 layer 1
            channel 3: player -1 layer 2
        """
        tensor = [
            [[0] * self.size for _ in range(self.size)]
            for _ in range(4)
        ]
        
        for row in range(self.size):
            for col in range(self.size):
                layer1, layer2 = self.board[row][col]
                
                if layer1 == 1:
                    tensor[0][row][col] = 1
                elif layer1 == -1:
                    tensor[2][row][col] = 1
                
                if layer2 == 1:
                    tensor[1][row][col] = 1
                elif layer2 == -1:
                    tensor[3][row][col] = 1
        
        return tensor
    
    def to_dict(self) -> dict:
        """盤面を辞書形式に変換"""
        return {
            "size": self.size,
            "board": [[cell[:] for cell in row] for row in self.board]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Board":
        """辞書から盤面を復元"""
        board = cls(size=data["size"])
        board.board = [[cell[:] for cell in row] for row in data["board"]]
        return board
    
    def clone(self) -> "Board":
        """盤面のディープコピーを作成"""
        new_board = Board(self.size)
        new_board.board = copy.deepcopy(self.board)
        return new_board
    
    def reset(self) -> None:
        """盤面をリセット"""
        self.board = [
            [[0, 0] for _ in range(self.size)] for _ in range(self.size)
        ]
    
    def count_tiles(self, player: Literal[1, -1]) -> dict:
        """
        プレイヤーのタイル数を数える
        
        Returns:
            {"layer1": count, "layer2": count, "total": count}
        """
        layer1_count = 0
        layer2_count = 0
        
        for row in range(self.size):
            for col in range(self.size):
                l1, l2 = self.board[row][col]
                if l1 == player:
                    layer1_count += 1
                if l2 == player:
                    layer2_count += 1
        
        return {
            "layer1": layer1_count,
            "layer2": layer2_count,
            "total": layer1_count + layer2_count
        }
    
    def get_edge_positions(self, player: Literal[1, -1], edge: str) -> List[Tuple[int, int]]:
        """
        指定したエッジにプレイヤーの色があるセルを取得
        
        Args:
            player: プレイヤー
            edge: "top", "bottom", "left", "right"
            
        Returns:
            セルのリスト [(row, col), ...]
        """
        positions = []
        
        if edge == "top":
            for col in range(self.size):
                if self.has_player_color(0, col, player):
                    positions.append((0, col))
        elif edge == "bottom":
            for col in range(self.size):
                if self.has_player_color(self.size - 1, col, player):
                    positions.append((self.size - 1, col))
        elif edge == "left":
            for row in range(self.size):
                if self.has_player_color(row, 0, player):
                    positions.append((row, 0))
        elif edge == "right":
            for row in range(self.size):
                if self.has_player_color(row, self.size - 1, player):
                    positions.append((row, self.size - 1))
        
        return positions
    
    def __str__(self) -> str:
        """盤面の文字列表現（デバッグ用）"""
        lines = []
        lines.append(f"Board({self.size}x{self.size})")
        
        for row in range(min(5, self.size)):  # 最初の5行のみ表示
            row_str = ""
            for col in range(min(10, self.size)):  # 最初の10列のみ表示
                l1, l2 = self.board[row][col]
                if l2 != 0:
                    row_str += f"[{l1},{l2}]"
                elif l1 != 0:
                    row_str += f"[{l1},_]"
                else:
                    row_str += "[_,_]"
            if self.size > 10:
                row_str += "..."
            lines.append(row_str)
        
        if self.size > 5:
            lines.append("...")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"Board(size={self.size})"

