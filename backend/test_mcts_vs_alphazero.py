"""
MCTS vs Alpha Zero 対戦テストスクリプト

MCTSとAlpha Zeroを戦わせて性能を比較します。
"""

import sys
import os
from pathlib import Path

# パス設定
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))
sys.path.append(os.path.join(backend_path, 'alpha_zero'))
sys.path.append(os.path.join(backend_path, 'alpha-zero-general'))

from game.game import WataruToGame
from mcts.mcts import create_mcts_engine, visualize_board
from alpha_zero.AlphaZeroPlayer import AlphaZeroPlayer


def play_game_mcts_vs_alphazero(
    board_size=9,
    mcts_time_limit=5.0,
    alphazero_sims=50,
    mcts_plays_first=True,
    verbose=False,
    show_board=False
):
    """
    MCTS vs Alpha Zeroで1ゲーム
    
    Args:
        board_size: 盤面サイズ
        mcts_time_limit: MCTSの思考時間制限（秒）
        alphazero_sims: Alpha ZeroのMCTSシミュレーション回数
        mcts_plays_first: Trueの場合MCTSが先手（水色）、Falseの場合Alpha Zeroが先手
        verbose: 詳細ログを表示
        show_board: 盤面を表示
        
    Returns:
        winner: 1=MCTS勝利, -1=Alpha Zero勝利, 0=引き分け
    """
    game = WataruToGame(board_size)
    mcts = create_mcts_engine(time_limit=mcts_time_limit, verbose=False)
    
    # Alpha Zero AIを初期化
    try:
        alphazero = AlphaZeroPlayer(
            model_path='alpha_zero/models/best.pth.tar',
            num_mcts_sims=alphazero_sims,
            board_size=board_size
        )
        print("Alpha Zero AI読み込み成功")
    except Exception as e:
        print(f"ERROR: Alpha Zero AI読み込み失敗: {e}")
        return None
    
    move_count = 0
    max_moves = 500  # 無限ループ防止
    
    # プレイヤー割り当て
    if mcts_plays_first:
        mcts_player = 1    # 水色
        az_player = -1     # ピンク
        mcts_name = "MCTS🔵"
        az_name = "AlphaZero🔴"
    else:
        mcts_player = -1   # ピンク
        az_player = 1      # 水色
        mcts_name = "MCTS🔴"
        az_name = "AlphaZero🔵"
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"対戦開始: {mcts_name} vs {az_name}")
        print(f"MCTS思考時間: {mcts_time_limit}秒")
        print(f"Alpha Zeroシミュレーション: {alphazero_sims}回")
        print(f"{'='*60}\n")
    
    # 初期盤面を表示
    if show_board:
        print(visualize_board(game, f"初期盤面"))
    
    while game.winner is None and move_count < max_moves:
        current_player_name = mcts_name if game.current_player == mcts_player else az_name
        
        if game.current_player == mcts_player:
            # MCTSの手番
            if verbose:
                print(f"ターン {move_count + 1}: {mcts_name} 思考中...", end=" ", flush=True)
            move = mcts.search(game)
            if move is None:
                if verbose:
                    print("合法手なし")
                break
            if verbose:
                print(f"完了")
                print(f"  {mcts_name} が選択: {move}")
        else:
            # Alpha Zeroの手番
            if verbose:
                print(f"ターン {move_count + 1}: {az_name} 思考中...", end=" ", flush=True)
            try:
                move = alphazero.get_move(game)
                if move is None:
                    if verbose:
                        print("合法手なし")
                    break
                if verbose:
                    print(f"完了")
                    print(f"  {az_name} が選択: {move}")
            except Exception as e:
                if verbose:
                    print(f"エラー: {e}")
                break
        
        success = game.apply_move(move)
        if not success:
            if verbose:
                print(f"  手の適用に失敗！")
            break
        move_count += 1
        
        # 手を打った後の盤面を表示
        if show_board:
            prev_player_name = mcts_name if game.current_player == az_player else az_name
            print(visualize_board(game, f"手 {move_count}: {prev_player_name} が打った後"))
    
    # 最終的な勝者を返す
    if verbose:
        print(f"\nゲーム終了: {move_count}手")
        if game.winner == mcts_player:
            print(f"勝者: {mcts_name}")
        elif game.winner == az_player:
            print(f"勝者: {az_name}")
        else:
            print(f"引き分け")
    
    # 最終盤面を表示
    if show_board and verbose:
        print(visualize_board(game, f"最終盤面"))
    
    if game.winner is None:
        if move_count >= max_moves:
            if verbose:
                print(f"最大手数到達（{max_moves}手）: 引き分け")
            return 0
        # 合法手がなくなった場合も引き分け
        return 0
    
    # 勝者を標準化（1=MCTS勝利, -1=Alpha Zero勝利, 0=引き分け）
    if game.winner == mcts_player:
        return 1  # MCTS勝利
    elif game.winner == az_player:
        return -1  # Alpha Zero勝利
    else:
        return 0  # 引き分け


def evaluate_mcts_vs_alphazero(
    num_games=10,
    board_size=9,
    mcts_time_limit=5.0,
    alphazero_sims=50
):
    """
    MCTS vs Alpha Zeroの対戦評価
    
    Args:
        num_games: 対戦回数（偶数を推奨。先手後手を入れ替えて対戦）
        board_size: 盤面サイズ
        mcts_time_limit: MCTSの思考時間制限
        alphazero_sims: Alpha ZeroのMCTSシミュレーション回数
    """
    print("=" * 60)
    print(f"MCTS vs Alpha Zero 評価")
    print("=" * 60)
    print(f"盤面サイズ: {board_size}x{board_size}")
    print(f"対戦回数: {num_games}")
    print(f"MCTS思考時間: {mcts_time_limit}秒")
    print(f"Alpha Zeroシミュレーション: {alphazero_sims}回")
    print("=" * 60)
    
    mcts_wins = 0
    alphazero_wins = 0
    draws = 0
    
    for i in range(num_games):
        # 先手後手を交互に入れ替え
        mcts_plays_first = (i % 2 == 0)
        
        print(f"\nゲーム {i+1}/{num_games}")
        if mcts_plays_first:
            print("  先手: MCTS (水色🔵), 後手: Alpha Zero (ピンク🔴)")
        else:
            print("  先手: Alpha Zero (水色🔵), 後手: MCTS (ピンク🔴)")
        
        winner = play_game_mcts_vs_alphazero(
            board_size=board_size,
            mcts_time_limit=mcts_time_limit,
            alphazero_sims=alphazero_sims,
            mcts_plays_first=mcts_plays_first,
            verbose=False
        )
        
        if winner is None:
            print(f"ゲーム {i+1}: エラー（スキップ）")
            continue
        
        if winner == 1:
            mcts_wins += 1
            print(f"ゲーム {i+1}: MCTS勝利！")
        elif winner == -1:
            alphazero_wins += 1
            print(f"ゲーム {i+1}: Alpha Zero勝利！")
        else:
            draws += 1
            print(f"ゲーム {i+1}: 引き分け")
    
    print("\n" + "=" * 60)
    print("結果サマリー")
    print("=" * 60)
    total_games = mcts_wins + alphazero_wins + draws
    if total_games > 0:
        print(f"MCTS勝利: {mcts_wins}/{total_games} ({mcts_wins/total_games*100:.1f}%)")
        print(f"Alpha Zero勝利: {alphazero_wins}/{total_games} ({alphazero_wins/total_games*100:.1f}%)")
        print(f"引き分け: {draws}/{total_games} ({draws/total_games*100:.1f}%)")
    print("=" * 60)


def quick_test(board_size=9, mcts_plays_first=True, show_board=False):
    """クイックテスト（1ゲーム）"""
    print("=" * 60)
    print(f"MCTS vs Alpha Zero クイックテスト")
    print(f"盤面: {board_size}x{board_size}")
    print(f"先手: {'MCTS' if mcts_plays_first else 'Alpha Zero'}")
    print("=" * 60)
    
    winner = play_game_mcts_vs_alphazero(
        board_size=board_size,
        mcts_time_limit=3.0,
        alphazero_sims=25,
        mcts_plays_first=mcts_plays_first,
        verbose=True,
        show_board=show_board
    )
    
    print("\n" + "=" * 60)
    if winner is None:
        print("結果: エラー")
    elif winner == 1:
        print("結果: MCTS勝利！")
    elif winner == -1:
        print("結果: Alpha Zero勝利！")
    else:
        print("結果: 引き分け")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCTS vs Alpha Zero 対戦テスト")
    parser.add_argument("--quick", action="store_true", help="クイックテスト（1ゲーム）")
    parser.add_argument("--games", type=int, default=10, help="評価ゲーム数（デフォルト: 10）")
    parser.add_argument("--mcts-time", type=float, default=5.0, help="MCTS思考時間（秒、デフォルト: 5.0）")
    parser.add_argument("--az-sims", type=int, default=50, help="Alpha Zeroシミュレーション回数（デフォルト: 50）")
    parser.add_argument("--size", type=int, default=9, help="盤面サイズ（デフォルト: 9）")
    parser.add_argument("--show-board", action="store_true", help="一手ごとに盤面を表示")
    parser.add_argument("--az-first", action="store_true", help="Alpha Zeroを先手にする")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test(
            board_size=args.size,
            mcts_plays_first=not args.az_first,
            show_board=args.show_board
        )
    else:
        evaluate_mcts_vs_alphazero(
            num_games=args.games,
            board_size=args.size,
            mcts_time_limit=args.mcts_time,
            alphazero_sims=args.az_sims
        )

