"""
MCTS AIのテストスクリプト

MCTSの動作を確認し、ランダムAIとの対戦で勝率を測定します。
"""

import sys
from pathlib import Path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from game.game import WataruToGame
from mcts.mcts import create_mcts_engine, visualize_board
import random


def play_game_random_vs_random(board_size=18):
    """ランダムAI vs ランダムAIで1ゲーム"""
    game = WataruToGame(board_size)
    
    while game.winner is None:
        moves = game.get_legal_moves()
        if not moves:
            break
        move = random.choice(moves)
        game.apply_move(move)
    
    return game.winner


def play_game_mcts_vs_random(board_size=9, time_limit=5.0, verbose=False, show_board=False):
    """MCTS AI vs ランダムAIで1ゲーム"""
    game = WataruToGame(board_size)
    mcts = create_mcts_engine(time_limit=time_limit, verbose=False)
    
    move_count = 0
    max_moves = 500  # 無限ループ防止（増やす）
    
    # 初期盤面を表示
    if show_board:
        print(visualize_board(game, f"初期盤面"))
    
    while game.winner is None and move_count < max_moves:
        if game.current_player == 1:
            # MCTS AIの手番（水色）
            if verbose:
                print(f"  ターン {move_count + 1}: MCTS思考中...", end=" ", flush=True)
            move = mcts.search(game)
            if move is None:
                if verbose:
                    print("合法手なし")
                break
            if verbose:
                print(f"完了")
                print(f"  MCTS が選択した手: {move}")
        else:
            # ランダムAIの手番（ピンク）
            moves = game.get_legal_moves()
            if not moves:
                if verbose:
                    print(f"  ターン {move_count + 1}: ランダムAI - 合法手なし")
                break
            move = random.choice(moves)
            if verbose:
                print(f"  ターン {move_count + 1}: ランダムAI が選択した手: {move}")
        
        success = game.apply_move(move)
        if not success:
            if verbose:
                print(f"  手の適用に失敗！")
            break
        move_count += 1
        
        # 手を打った後の盤面を表示
        if show_board:
            player_name = "水色🔵(MCTS)" if game.current_player == -1 else "ピンク🔴(Random)"
            prev_player = "水色🔵(MCTS)" if game.current_player == 1 else "ピンク🔴(Random)"
            print(visualize_board(game, f"手 {move_count}: {prev_player} が打った後"))
    
    # 最終的な勝者を返す
    if verbose:
        print(f"  ゲーム終了: {move_count}手")
        if game.winner == 1:
            print(f"  勝者: MCTS (水色)")
        elif game.winner == -1:
            print(f"  勝者: ランダム (ピンク)")
        else:
            print(f"  勝者: 引き分け")
    
    # 最終盤面を表示
    if show_board and verbose:
        print(visualize_board(game, f"最終盤面"))
    
    if game.winner is None:
        if move_count >= max_moves:
            if verbose:
                print(f"  最大手数到達（{max_moves}手）: 引き分け")
            return 0
        # 合法手がなくなった場合も引き分け
        return 0
    
    return game.winner


def evaluate_mcts(num_games=10, board_size=9, time_limit=5.0):
    """
    MCTSの性能を評価
    
    Args:
        num_games: 対戦回数
        board_size: 盤面サイズ
        time_limit: MCTSの思考時間制限
    """
    print("=" * 60)
    print(f"MCTS評価（{board_size}x{board_size}盤面、{num_games}ゲーム、思考時間{time_limit}秒）")
    print("=" * 60)
    
    wins = 0
    losses = 0
    draws = 0
    
    for i in range(num_games):
        print(f"\nゲーム {i+1}/{num_games} プレイ中...")
        winner = play_game_mcts_vs_random(board_size=board_size, time_limit=time_limit)
        
        if winner == 1:
            wins += 1
            print(f"ゲーム {i+1}: MCTS勝利！")
        elif winner == -1:
            losses += 1
            print(f"ゲーム {i+1}: ランダム勝利")
        else:
            draws += 1
            print(f"ゲーム {i+1}: 引き分け")
    
    print("\n" + "=" * 60)
    print("結果サマリー")
    print("=" * 60)
    print(f"MCTS勝利: {wins}/{num_games} ({wins/num_games*100:.1f}%)")
    print(f"ランダム勝利: {losses}/{num_games} ({losses/num_games*100:.1f}%)")
    print(f"引き分け: {draws}/{num_games} ({draws/num_games*100:.1f}%)")
    print("=" * 60)


def quick_test(board_size=9, show_board=False):
    """クイックテスト（1ゲーム）"""
    print("=" * 60)
    print(f"クイックテスト開始（{board_size}x{board_size}盤面、1ゲーム、3秒思考）")
    print("=" * 60)
    
    winner = play_game_mcts_vs_random(board_size=board_size, time_limit=3.0, verbose=True, show_board=show_board)
    
    print("\n" + "=" * 60)
    if winner == 1:
        print("結果: MCTS勝利！")
    elif winner == -1:
        print("結果: ランダム勝利")
    else:
        print("結果: 引き分け")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCTS AIのテストと評価")
    parser.add_argument("--quick", action="store_true", help="クイックテスト（1ゲーム）")
    parser.add_argument("--games", type=int, default=10, help="評価ゲーム数（デフォルト: 10）")
    parser.add_argument("--time", type=float, default=5.0, help="思考時間制限（秒、デフォルト: 5.0）")
    parser.add_argument("--size", type=int, default=9, help="盤面サイズ（デフォルト: 9）")
    parser.add_argument("--show-board", action="store_true", help="一手ごとに盤面を表示")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test(board_size=args.size, show_board=args.show_board)
    else:
        evaluate_mcts(num_games=args.games, board_size=args.size, time_limit=args.time)

