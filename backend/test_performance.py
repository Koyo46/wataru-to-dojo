"""
パフォーマンステスト

get_legal_moves()の速度を測定します。
"""

import sys
from pathlib import Path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from game.game import WataruToGame
import time


def test_legal_moves_performance(board_size=9, iterations=100):
    """get_legal_moves()の性能を測定"""
    print("=" * 60)
    print(f"パフォーマンステスト: {board_size}x{board_size}盤面")
    print("=" * 60)
    
    game = WataruToGame(board_size)
    
    # ウォームアップ
    _ = game.get_legal_moves()
    
    # 測定開始（キャッシュなし - 毎回無効化）
    start_time = time.time()
    
    for _ in range(iterations):
        game._cache_valid = False  # キャッシュを無効化して本当の速度を測定
        moves = game.get_legal_moves()
    
    elapsed_time = time.time() - start_time
    
    # キャッシュありの測定（実際のキャッシュヒット率を測定）
    # 新しいゲームを作って、最初の1回だけ計算、残りはキャッシュヒット
    game2 = WataruToGame(board_size)
    cache_start = time.time()
    for i in range(iterations):
        if i == 0:
            game2._cache_valid = False  # 最初だけキャッシュミス
        moves = game2.get_legal_moves()  # 2回目以降はキャッシュヒット
    cache_elapsed = time.time() - cache_start
    
    # 実際の1回のキャッシュヒット時間を測定
    # Windowsのタイマー精度を考慮して、より多くの回数で測定
    cache_test_iterations = iterations * 100  # 100倍実行
    game3 = WataruToGame(board_size)
    game3.get_legal_moves()  # キャッシュを作成
    pure_cache_start = time.time()
    for _ in range(cache_test_iterations):
        moves = game3.get_legal_moves()  # 純粋なキャッシュヒット
    pure_cache_elapsed = time.time() - pure_cache_start
    pure_cache_per_call = pure_cache_elapsed / cache_test_iterations
    
    # 結果表示
    moves_count = len(moves)
    calls_per_sec = iterations / elapsed_time if elapsed_time > 0 else float('inf')
    cache_calls_per_sec = 1 / pure_cache_per_call if pure_cache_per_call > 0 else float('inf')
    speedup = (elapsed_time/iterations) / pure_cache_per_call if pure_cache_per_call > 0 else float('inf')
    
    print(f"\n結果:")
    print(f"  合法手の数: {moves_count}手")
    print(f"  実行回数: {iterations}回")
    print(f"\n【キャッシュなし（毎回再計算）】")
    print(f"  実行時間: {elapsed_time:.3f}秒")
    print(f"  呼び出し/秒: {calls_per_sec:.1f}回/秒")
    print(f"  1回あたり: {elapsed_time/iterations*1000:.2f}ミリ秒")
    print(f"\n【キャッシュあり（純粋なキャッシュヒット）】")
    print(f"  実行時間: {pure_cache_elapsed:.6f}秒 ({cache_test_iterations}回)")
    print(f"  呼び出し/秒: {cache_calls_per_sec:.0f}回/秒")
    print(f"  1回あたり: {pure_cache_per_call*1000000:.2f}マイクロ秒")
    
    # 高速化率の表示（ゼロ除算対策）
    if speedup == float('inf'):
        print(f"\n高速化率: 測定不能（キャッシュが極めて高速）")
    else:
        print(f"\n高速化率: {speedup:.0f}倍")
    print("=" * 60)
    
    return calls_per_sec


def test_mcts_simulation_speed(board_size=9, time_limit=5.0):
    """MCTSのシミュレーション速度を測定"""
    print("\n" + "=" * 60)
    print(f"MCTSシミュレーション速度テスト: {board_size}x{board_size}盤面")
    print("=" * 60)
    
    from mcts.mcts import create_mcts_engine
    
    game = WataruToGame(board_size)
    mcts = create_mcts_engine(time_limit=time_limit, verbose=False)
    
    print(f"\n思考時間: {time_limit}秒")
    start_time = time.time()
    move = mcts.search(game)
    elapsed_time = time.time() - start_time
    
    print(f"\n結果:")
    print(f"  シミュレーション回数: {mcts.stats.simulations_run}回")
    print(f"  探索ノード数: {mcts.stats.nodes_explored}個")
    print(f"  実行時間: {elapsed_time:.2f}秒")
    print(f"  シミュレーション/秒: {mcts.stats.simulations_run/elapsed_time:.1f}回/秒")
    print(f"  選択された手: {move}")
    print("=" * 60)
    
    return mcts.stats.simulations_run / elapsed_time


if __name__ == "__main__":
    print("\nパフォーマンステスト開始\n")
    
    # 9x9盤面テスト
    print("【テスト1】get_legal_moves()の速度（9x9）")
    speed_9x9 = test_legal_moves_performance(board_size=9, iterations=100)
    
    # 18x18盤面テスト
    print("\n【テスト2】get_legal_moves()の速度（18x18）")
    speed_18x18 = test_legal_moves_performance(board_size=18, iterations=50)
    
    # MCTSテスト
    print("\n【テスト3】MCTSシミュレーション速度（9x9、5秒）")
    mcts_speed = test_mcts_simulation_speed(board_size=9, time_limit=5.0)
    
    print("\n" + "=" * 60)
    print("サマリー")
    print("=" * 60)
    print(f"9x9 合法手生成: {speed_9x9:.1f}回/秒")
    print(f"18x18 合法手生成: {speed_18x18:.1f}回/秒")
    print(f"MCTS (9x9, 5秒): {mcts_speed:.1f}シミュレーション/秒")
    print("=" * 60)
    
    # 期待値との比較
    print("\n【期待値との比較】")
    if mcts_speed > 100:
        print(f"EXCELLENT! {mcts_speed:.0f}回/秒は非常に高速です")
    elif mcts_speed > 50:
        print(f"GOOD! {mcts_speed:.0f}回/秒は良好です")
    elif mcts_speed > 20:
        print(f"OK. {mcts_speed:.0f}回/秒はまあまあです（さらに最適化可能）")
    else:
        print(f"SLOW. {mcts_speed:.0f}回/秒は遅いです（要最適化）")
    print()

