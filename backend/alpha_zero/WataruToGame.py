"""
ワタルートゲーム - Alpha Zero General 互換ラッパー

alpha-zero-generalのGame抽象クラスに準拠したワタルートゲームの実装
"""

import sys
import os

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import WataruToGame as OriginalGame
from game.move import Move
import numpy as np
from typing import List, Tuple, Optional


class WataruToGame:
    """
    Alpha Zero General用のワタルートゲームラッパー
    
    このクラスは、alpha-zero-generalフレームワークと
    既存のワタルートゲームロジックを橋渡しします。
    """
    
    def __init__(self, board_size: int = 9):
        """
        Args:
            board_size: 盤面サイズ（デフォルト: 9x9）
                       小さな盤面で学習を開始することを推奨
        """
        self.board_size = board_size
        
        # アクション空間の計算（レイヤー情報を含む）
        # 各マスに対して: 向き(2) x サイズ(3: 3/4/5マス) x レイヤー(2) = 12通り
        # 全体: 12 * board_size^2
        # レイヤー0: レイヤー1モード（通常配置）
        # レイヤー1: レイヤー2モード（橋渡し）
        self.action_size = 12 * board_size * board_size
    
    def getInitBoard(self) -> OriginalGame:
        """
        初期盤面を返す
        
        Returns:
            WataruToGameオブジェクト（初期状態）
        """
        return OriginalGame(board_size=self.board_size)
    
    def getBoardSize(self) -> Tuple[int, int]:
        """
        盤面サイズを返す
        
        Returns:
            (rows, cols): 盤面の行数と列数
        """
        return (self.board_size, self.board_size)
    
    def getActionSize(self) -> int:
        """
        可能なアクション数を返す
        
        Returns:
            アクション数（各マスに対して向き2×サイズ2）
        """
        return self.action_size
    
    def getNextState(self, board: OriginalGame, player: int, action: int) -> Tuple[OriginalGame, int]:
        """
        次の状態を返す
        
        Args:
            board: 現在の盤面
            player: 現在のプレイヤー (1 or -1)
            action: 選択されたアクション
            
        Returns:
            (next_board, next_player): 次の盤面と次のプレイヤー
        """
        # 盤面のクローンを作成
        next_board = board.clone()
        
        # アクションをMoveオブジェクトに変換
        move = self._action_to_move(action, next_board)
        
        # 無効な手の場合 - これは起こらないはずだが念のため
        if move is None:
            print(f"WARNING: None move for action {action}")
            # ゲームを強制終了
            next_board.winner = -player  # 相手の勝ち
            return (next_board, -player)
        
        # 手を適用
        success = False
        error_msg = None
        try:
            success = next_board.apply_move(move)
        except Exception as e:
            error_msg = str(e)
            print(f"Invalid move: {error_msg}")
            success = False
        
        # 手が適用できなかった場合
        if not success:
            # デバッグ情報を出力
            if error_msg is None:
                print(f"Invalid move: apply_move returned False for action {action}")
                print(f"  Move: size={move.block_size}, dir={move.direction}, start={move.start_position}")
                print(f"  Player blocks: size4={next_board.player_blocks[player].size4}, size5={next_board.player_blocks[player].size5}")
            
            # この手を選んだプレイヤーの負けとする
            next_board.winner = -player
            return (next_board, -player)
        
        # 次のプレイヤーは常に反対側
        return (next_board, -player)
    
    def getValidMoves(self, board: OriginalGame, player: int) -> np.ndarray:
        """
        合法手のマスクを返す
        
        Args:
            board: 現在の盤面
            player: 現在のプレイヤー
            
        Returns:
            valid_moves: 長さaction_sizeのバイナリベクトル
                        (1=合法, 0=非合法)
        """
        valid_moves = np.zeros(self.action_size, dtype=np.uint8)
        
        # ゲームが既に終了している場合
        if board.winner is not None:
            return valid_moves
        
        # 合法手を取得（初手フィルタリングは無効: 3マスブロックも含める）
        legal_moves = board.get_legal_moves(filter_opening=False)
        
        # 合法手が無い場合は強制的にゲーム終了
        if len(legal_moves) == 0:
            # ゲーム終了判定を実行してwinnerを設定
            self.getGameEnded(board, player)
            return valid_moves
        
        # デバッグ: 最初の数手をログ出力
        debug = False
        if debug and len(legal_moves) > 0:
            print(f"\ngetValidMoves: {len(legal_moves)} legal moves")
            for i, move in enumerate(legal_moves[:3]):  # 最初の3手のみ
                action_id = self._move_to_action(move)
                print(f"  Move {i}: size={move.block_size}, dir={move.direction}, start=({move.start_position.row},{move.start_position.col},L{move.start_position.layer}) -> action={action_id}")
        
        # 各合法手をアクションIDに変換してマーク
        conversion_errors = 0
        for move in legal_moves:
            try:
                action_id = self._move_to_action(move)
                if 0 <= action_id < self.action_size:
                    valid_moves[action_id] = 1
                else:
                    conversion_errors += 1
            except Exception as e:
                # エラーが発生した場合はスキップ（デバッグ用に記録）
                conversion_errors += 1
                # print(f"Warning: Failed to convert move to action: {e}")
                continue
        
        if conversion_errors > 0:
            print(f"WARNING: {conversion_errors} moves failed to convert to actions")
        
        # もし何らかの理由でvalid_movesがすべて0の場合
        if np.sum(valid_moves) == 0:
            print("WARNING: No valid moves after conversion!")
            print(f"  Original legal_moves count: {len(legal_moves)}")
            # ゲーム終了判定を実行
            self.getGameEnded(board, player)
        
        return valid_moves
    
    def getGameEnded(self, board: OriginalGame, player: int) -> float:
        """
        ゲーム終了判定
        
        Args:
            board: 現在の盤面
            player: 現在のプレイヤー (1 or -1)
            
        Returns:
            0: ゲーム継続中
            1: playerの勝利
            -1: playerの敗北
            小さな値: 引き分け
        """
        # 既に勝者が決まっている場合
        if board.winner is not None:
            if board.winner == 0:
                # 引き分け
                return 1e-4
            elif board.winner == player:
                # playerの勝利
                return 1
            else:
                # playerの敗北
                return -1
        
        # 合法手が無い場合は強制的にゲーム終了とみなす
        # （ブロックを使い切った場合など）
        legal_moves = board.get_legal_moves(filter_opening=False)
        if len(legal_moves) == 0:
            # 合法手がない場合は現在のスコアで判定
            # 便宜的に、より多くの陣地を取っている方を勝ちとする
            p1_tiles = board.board.count_tiles(1)
            p_neg1_tiles = board.board.count_tiles(-1)
            
            p1_total = p1_tiles['layer1'] + p1_tiles['layer2']
            p_neg1_total = p_neg1_tiles['layer1'] + p_neg1_tiles['layer2']
            
            if p1_total > p_neg1_total:
                winner = 1
            elif p_neg1_total > p1_total:
                winner = -1
            else:
                winner = 0  # 引き分け
            
            # 勝者を設定
            board.winner = winner
            
            if winner == 0:
                return 1e-4
            elif winner == player:
                return 1
            else:
                return -1
        
        # ゲーム継続中
        return 0
    
    def getCanonicalForm(self, board: OriginalGame, player: int) -> OriginalGame:
        """
        常に現在のプレイヤー視点に正規化した盤面を返す
        
        ワタルートでは、盤面の対称性が複雑なため、
        シンプルにそのまま返す実装にする
        
        Args:
            board: 現在の盤面
            player: 現在のプレイヤー (1 or -1)
            
        Returns:
            canonical_board: 正規化された盤面
        """
        # シンプルにそのまま返す
        # Alpha Zeroでは通常、常に現在のプレイヤー視点に正規化するが、
        # ワタルートの場合は盤面をそのまま使い、プレイヤー情報で判断する
        return board
    
    def getSymmetries(self, board: OriginalGame, pi: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        対称性を利用したデータ拡張
        
        盤面の回転・反転により8パターンのデータを生成
        （データ拡張により学習効率向上）
        
        Args:
            board: 現在の盤面
            pi: 方策ベクトル（各アクションの確率）
            
        Returns:
            symmetries: [(board_tensor, pi)] のリスト
            ※ board_tensor は numpy配列 (6, board_size, board_size)
        """
        # 盤面をテンソル形式に変換
        board_tensor = self._board_to_tensor(board)
        
        # TODO: 対称性の実装
        # 現時点では対称性を使わない（シンプルな実装）
        # 将来的には、90度回転×4 + 反転×2 = 8パターンを生成
        
        return [(board_tensor, pi)]
    
    def _board_to_tensor(self, board: OriginalGame) -> np.ndarray:
        """
        盤面をテンソル形式に変換（内部用ヘルパー）
        
        Args:
            board: WataruToGameオブジェクト
        
        Returns:
            tensor: (6, board_size, board_size) の numpy配列
                   チャンネル0-3: 盤面（P1層1, P1層2, P-1層1, P-1層2）
                   チャンネル4-5: 残りブロック情報
        """
        # 盤面の基本テンソル（4チャンネル）
        board_tensor = board.get_board_as_tensor()  # (4, size, size)
        board_tensor = np.array(board_tensor, dtype=np.float32)
        
        # 残りブロック情報（2チャンネル）を追加
        blocks_channel = np.zeros((2, self.board_size, self.board_size), dtype=np.float32)
        
        # プレイヤー1の残りブロック情報
        p1_blocks = board.player_blocks[1]
        blocks_channel[0, :, :] = (p1_blocks.size4 + p1_blocks.size5) / 2.0
        
        # プレイヤー-1の残りブロック情報
        p_neg1_blocks = board.player_blocks[-1]
        blocks_channel[1, :, :] = (p_neg1_blocks.size4 + p_neg1_blocks.size5) / 2.0
        
        # 結合 (6, size, size)
        full_tensor = np.concatenate([board_tensor, blocks_channel], axis=0)
        
        return full_tensor
    
    def stringRepresentation(self, board: OriginalGame) -> str:
        """
        盤面の文字列表現（キャッシュ・ハッシュ用）
        
        MCTSのトランスポジションテーブルで使用
        
        Args:
            board: 現在の盤面
            
        Returns:
            board_string: 盤面の文字列表現
        """
        # 盤面を簡潔に文字列化（高速化のため）
        # move_historyは除外（同じ盤面状態なら同じハッシュにする）
        
        # 盤面の状態を取得
        board_array = board.board.board
        
        # 盤面を文字列化（NumPy風の簡潔な形式）
        board_str = ""
        for row in board_array:
            for cell in row:
                board_str += f"{cell[0]},{cell[1]};"
        
        # プレイヤーと残りブロックを追加
        player_str = str(board.current_player)
        blocks_str = f"{board.player_blocks[1].size4},{board.player_blocks[1].size5},{board.player_blocks[-1].size4},{board.player_blocks[-1].size5}"
        
        return f"{board_str}|{player_str}|{blocks_str}"
    
    def display(self, board: OriginalGame) -> None:
        """
        盤面を表示（デバッグ用）
        
        Args:
            board: 表示する盤面
        """
        print("\n現在の盤面:")
        print(f"プレイヤー: {'水色(1)' if board.current_player == 1 else 'ピンク(-1)'}")
        print(f"残りブロック - P1: {board.player_blocks[1].to_dict()}, P-1: {board.player_blocks[-1].to_dict()}")
        
        # 簡易的な盤面表示
        for row in range(self.board_size):
            row_str = ""
            for col in range(self.board_size):
                layer1, layer2 = board.board.board[row][col]
                if layer1 == 0 and layer2 == 0:
                    row_str += " . "
                elif layer2 != 0:
                    row_str += f" {layer2:+1d}2"
                else:
                    row_str += f" {layer1:+1d}1"
            print(row_str)
        
        if board.winner is not None:
            if board.winner == 0:
                print("\n結果: 引き分け")
            else:
                print(f"\n勝者: {'水色(1)' if board.winner == 1 else 'ピンク(-1)'}")
    
    # ========== ヘルパーメソッド ==========
    
    def _move_to_action(self, move: Move) -> int:
        """
        MoveオブジェクトをアクションIDに変換
        
        アクション空間のエンコーディング（レイヤー情報を含む）:
        action_id = ((direction * 3 + size) * 2 + layer) * (board_size^2) + position
        
        - direction: 0=vertical, 1=horizontal
        - size: 0=3マス, 1=4マス, 2=5マス
        - layer: 0=レイヤー1, 1=レイヤー2（橋渡し）
        - position: row * board_size + col
        
        **重要な制限**: 現在のアクション空間は、すべてのマスが同じレイヤーに配置される手のみをサポート。
        混合レイヤーの手（橋渡しモードで自分のマスを経由する手）は除外。
        
        Args:
            move: Moveオブジェクト
            
        Returns:
            action_id: アクションID (0 ~ action_size-1)
            
        Raises:
            ValueError: 変換できない手の場合（混合レイヤーなど）
        """
        # pathのすべての要素が同じレイヤーか確認
        first_layer = move.path[0].layer
        if not all(pos.layer == first_layer for pos in move.path):
            # 混合レイヤーの手は現在のアクション空間では表現できない
            raise ValueError(f"Mixed-layer moves are not supported in current action space")
        
        # 方向をインデックスに変換
        direction_idx = 0 if move.direction == 'vertical' else 1
        
        # サイズをインデックスに変換（block_sizeプロパティを使用）
        # 3マス=0, 4マス=1, 5マス=2
        if move.block_size == 3:
            size_idx = 0
        elif move.block_size == 4:
            size_idx = 1
        elif move.block_size == 5:
            size_idx = 2
        else:
            raise ValueError(f"Invalid block size: {move.block_size}")
        
        # レイヤーをインデックスに変換
        start_pos = move.start_position
        layer_idx = start_pos.layer  # 0=レイヤー1, 1=レイヤー2
        
        # 開始位置をインデックスに変換
        position = start_pos.row * self.board_size + start_pos.col
        
        # アクションIDを計算（レイヤー情報を含む）
        # エンコード: ((direction * 3 + size) * 2 + layer) * board_size^2 + position
        action_id = ((direction_idx * 3 + size_idx) * 2 + layer_idx) * (self.board_size ** 2) + position
        
        return action_id
    
    def _action_to_move(self, action: int, board: OriginalGame) -> Move:
        """
        アクションIDをMoveオブジェクトに変換（レイヤー情報を含む）
        
        デコード順序:
        1. position = action % (board_size^2)
        2. action //= (board_size^2)
        3. layer = action % 2
        4. action //= 2
        5. size = action % 3  (0=3マス, 1=4マス, 2=5マス)
        6. direction = action // 3
        
        Args:
            action: アクションID
            board: 現在の盤面（プレイヤー情報取得用）
            
        Returns:
            move: Moveオブジェクト（無効な場合はNone）
        """
        from game.move import Position
        from datetime import datetime
        
        # アクションIDをデコード
        position = action % (self.board_size ** 2)
        action //= (self.board_size ** 2)
        
        layer_idx = action % 2
        action //= 2
        
        size_idx = action % 3
        direction_idx = action // 3
        
        # 位置を行・列に変換
        row = position // self.board_size
        col = position % self.board_size
        
        # 方向を文字列に変換
        direction = 'vertical' if direction_idx == 0 else 'horizontal'
        
        # サイズを数値に変換 (0=3マス, 1=4マス, 2=5マス)
        if size_idx == 0:
            size = 3
        elif size_idx == 1:
            size = 4
        else:
            size = 5
        
        # レイヤーを数値に変換
        layer = layer_idx  # 0 or 1
        
        # 境界チェック：盤面外に出る場合はNoneを返す
        if direction == 'vertical':
            if row + size > self.board_size:
                return None
        else:  # horizontal
            if col + size > self.board_size:
                return None
        
        # pathを生成（レイヤー情報を含む）
        path = []
        for i in range(size):
            if direction == 'vertical':
                path.append(Position(row=row + i, col=col, layer=layer))
            else:  # horizontal
                path.append(Position(row=row, col=col + i, layer=layer))
        
        return Move(
            player=board.current_player,
            path=path,
            timestamp=datetime.now().timestamp()
        )


def quick_test():
    """簡易テスト"""
    print("=" * 60)
    print("WataruToGame ラッパー テスト")
    print("=" * 60)
    
    game = WataruToGame(board_size=9)
    
    print(f"\n盤面サイズ: {game.getBoardSize()}")
    print(f"アクション数: {game.getActionSize()}")
    
    # 初期盤面
    board = game.getInitBoard()
    print(f"\n初期プレイヤー: {board.current_player}")
    
    # 合法手
    valid_moves = game.getValidMoves(board, 1)
    print(f"合法手の数: {np.sum(valid_moves)}")
    
    # 最初の合法手を実行
    first_action = np.where(valid_moves == 1)[0][0]
    print(f"\n最初の合法手のアクションID: {first_action}")
    
    next_board, next_player = game.getNextState(board, 1, first_action)
    print(f"次のプレイヤー: {next_player}")
    
    # ゲーム終了判定
    result = game.getGameEnded(next_board, next_player)
    print(f"ゲーム終了: {result == 0 and 'いいえ' or 'はい'}")
    
    print("\nテスト完了！")


if __name__ == "__main__":
    quick_test()

