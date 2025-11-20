"""
プレイアウトの視覚化テストスクリプト

MCTSのシミュレーション中にどこに打っているかを確認するためのテストスクリプト
"""

import sys
from pathlib import Path

# バックエンドのパスを追加
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from game.game import WataruToGame
from mcts.mcts import create_mcts_engine


def test_playout_visualization():
    """プレイアウトの視覚化をテスト"""
    
    print("="*60)
    print("プレイアウト視覚化テスト")
    print("="*60)
    print("\nこのテストでは、MCTSのシミュレーション（プレイアウト）中に")
    print("実際にどこに手を打っているかを視覚化します。")
    print("\n最初の1回のシミュレーションのみを詳細表示します。")
    print("="*60)
    
    # ゲームを初期化
    game = WataruToGame(board_size=18)
    
    # 何手か進めてから確認（空の盤面だと合法手が多すぎるため）
    print("\n初期局面からいくつか手を進めます...")
    
    # 水色の手
    from game.move import Move, Position
    from datetime import datetime
    
    move1 = Move(
        player=1,
        path=[
            Position(8, 8, 0),
            Position(8, 9, 0),
            Position(8, 10, 0),
        ],
        timestamp=datetime.now().timestamp()
    )
    game.apply_move(move1)
    print(f"水色: {move1}")
    
    # ピンクの手
    move2 = Move(
        player=-1,
        path=[
            Position(9, 8, 0),
            Position(9, 9, 0),
            Position(9, 10, 0),
        ],
        timestamp=datetime.now().timestamp()
    )
    game.apply_move(move2)
    print(f"ピンク: {move2}")
    
    print("\n" + "="*60)
    print("現在の局面から、MCTS探索を開始します")
    print("最初の1回のシミュレーションを詳細表示します")
    print("="*60 + "\n")
    
    # MCTSエンジンを作成（デバッグモード有効）
    mcts = create_mcts_engine(
        time_limit=2.0,  # 短めに設定
        max_simulations=50,  # 少なめに設定
        verbose=True,
        use_tactical_heuristics=True,  # Tacticalモード
        debug_playout=True,  # プレイアウトデバッグ有効
        debug_playout_count=1  # 最初の1回のみ表示
    )
    
    # 探索実行
    best_move = mcts.search(game)
    
    print("\n" + "="*60)
    print("探索完了")
    print("="*60)
    print(f"\n最良の手: {best_move}")
    print(f"シミュレーション回数: {mcts.stats.simulations_run}")
    print(f"探索時間: {mcts.stats.time_elapsed:.2f}秒")
    

def test_pure_random_playout():
    """Pure Randomモードのプレイアウトをテスト"""
    
    print("\n\n" + "="*60)
    print("Pure Random プレイアウトテスト")
    print("="*60)
    print("\n完全ランダムなプレイアウトを視覚化します。")
    print("="*60)
    
    # ゲームを初期化
    game = WataruToGame(board_size=18)
    
    # MCTSエンジンを作成（Pure Randomモード）
    mcts = create_mcts_engine(
        time_limit=1.0,
        max_simulations=10,
        verbose=False,
        use_tactical_heuristics=False,  # Pure Randomモード
        debug_playout=True,
        debug_playout_count=1
    )
    
    # 探索実行
    best_move = mcts.search(game)
    
    print("\n探索完了")
    print(f"最良の手: {best_move}")


if __name__ == "__main__":
    # Tacticalモードのテスト
    test_playout_visualization()
    
    # Pure Randomモードのテスト（オプション）
    # test_pure_random_playout()
    
    print("\n" + "="*60)
    print("テスト完了！")
    print("="*60)
    print("\nこのスクリプトをカスタマイズして:")
    print("- debug_playout_count を増やして複数のシミュレーションを見る")
    print("- 特定の局面から始める")
    print("- Pure Random vs Tactical の違いを比較する")
    print("などができます。")
    print("="*60)

