"""
Alpha Zero AIプレイヤー

学習済みモデルを使って実際のゲームで対戦するためのクラス
"""

import sys
import os
import numpy as np

# パス設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'alpha-zero-general'))

from alpha_zero.WataruToGame import WataruToGame as GameWrapper
from alpha_zero.pytorch.NNet import NNetWrapper as NNet
from alpha_zero.DepthLimitedMCTS import DepthLimitedMCTS
from game.game import WataruToGame
from game.move import Move
from utils import dotdict


class AlphaZeroPlayer:
    """
    Alpha Zero AIプレイヤー
    
    学習済みモデルを使って手を選択
    """
    
    def __init__(self, model_path='alpha_zero/models/best.pth.tar', num_mcts_sims=50, board_size=9):
        """
        初期化
        
        Args:
            model_path: 学習済みモデルのパス
            num_mcts_sims: MCTSシミュレーション回数（多いほど強いが遅い）
            board_size: 盤面サイズ
        """
        self.board_size = board_size
        self.num_mcts_sims = num_mcts_sims
        
        # ゲームラッパーの作成
        self.game_wrapper = GameWrapper(board_size=board_size)
        
        # ニューラルネットの設定
        # 注意: 学習時の設定と一致させる必要がある
        args = dotdict({
            'lr': 0.001,
            'dropout': 0.3,
            'epochs': 10,
            'batch_size': 64,
            'num_channels': 96,         # 学習時の設定に合わせる（64→96）
            'num_res_blocks': 6,        # 学習時の設定に合わせる（4→6）
            'cuda': True,  # GPUを使用
            'checkpoint': './alpha_zero/models/',
        })
        
        # ニューラルネットの作成とモデル読み込み
        self.nnet = NNet(self.game_wrapper, args)
        
        try:
            # モデルファイルのパスを解決
            if not os.path.isabs(model_path):
                model_path = os.path.join(os.path.dirname(__file__), '..', model_path)
            
            folder = os.path.dirname(model_path)
            filename = os.path.basename(model_path)
            
            self.nnet.load_checkpoint(folder=folder, filename=filename)
            print(f"✅ Alpha Zeroモデル読み込み成功: {model_path}")
        except Exception as e:
            print(f"WARNING: モデル読み込み失敗: {e}")
            print("ランダムな初期重みで動作します")
        
        # MCTS設定
        mcts_args = dotdict({
            'numMCTSSims': num_mcts_sims,
            'cpuct': 1.0,
            'max_depth': 30,
        })
        
        self.mcts = DepthLimitedMCTS(self.game_wrapper, self.nnet, mcts_args)
        
        print(f"OK: Alpha Zero AIプレイヤー作成完了")
        print(f"   MCTSシミュレーション回数: {num_mcts_sims}")
        print(f"   盤面サイズ: {board_size}x{board_size}")
    
    def get_move(self, game: WataruToGame) -> Move:
        """
        現在の盤面から最善手を取得
        
        Args:
            game: 現在のゲーム状態
        
        Returns:
            選択された手（Moveオブジェクト）
        """
        # ゲームの状態をラッパーで扱える形式に変換（既にWataruToGameオブジェクト）
        # MCTSで手の確率分布を取得
        canonical_board = self.game_wrapper.getCanonicalForm(game, game.current_player)
        
        # MCTSの統計をリセット
        self.mcts.reset_stats()
        
        # 温度パラメータ0（貪欲）で最善手を選択
        action_probs = self.mcts.getActionProb(canonical_board, temp=0)
        
        # 最も確率の高いアクションを選択
        action = np.argmax(action_probs)
        
        # アクションをMoveオブジェクトに変換
        move = self.game_wrapper._action_to_move(action, game)
        
        # デバッグ情報
        stats = self.mcts.get_stats()
        print(f"Alpha Zero思考:")
        print(f"  選択アクション: {action}")
        print(f"  探索深さ: {stats['max_depth_reached']}")
        print(f"  探索状態数: {stats['total_states']}")
        
        return move
    
    def get_move_with_time_limit(self, game: WataruToGame, time_limit_ms: int = 5000) -> Move:
        """
        時間制限付きで手を取得
        
        Args:
            game: 現在のゲーム状態
            time_limit_ms: 思考時間制限（ミリ秒）
        
        Returns:
            選択された手（Moveオブジェクト）
        """
        # TODO: 時間制限の実装（反復深化MCTSなど）
        # 現時点ではシミュレーション回数固定
        return self.get_move(game)


def test_alpha_zero_player():
    """動作テスト"""
    print("=" * 60)
    print("Alpha Zero AIプレイヤー テスト")
    print("=" * 60)
    
    # AIプレイヤーの作成
    try:
        ai = AlphaZeroPlayer(num_mcts_sims=25)
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # テストゲームの作成
    game = WataruToGame(board_size=9)
    
    print("\n初期盤面で手を取得...")
    try:
        move = ai.get_move(game)
        print(f"\nOK: AIの手:")
        print(f"  サイズ: {move.block_size}マス")
        print(f"  方向: {move.direction}")
        print(f"  開始位置: ({move.start_position.row}, {move.start_position.col})")
        print(f"  レイヤー: {move.start_position.layer}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nテスト完了！")


if __name__ == "__main__":
    test_alpha_zero_player()

