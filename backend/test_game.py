"""
ゲームロジックの簡易テストスクリプト

基本的な動作確認を行います。
"""

from game.game import WataruToGame
from game.move import Move, Position


def test_basic_game():
    """基本的なゲームフローのテスト"""
    print("=== ワタルートゲーム テスト ===\n")
    
    # ゲームを作成
    game = WataruToGame(board_size=18)
    print(f"✓ ゲーム作成: {game.board.size}x{game.board.size}")
    print(f"  現在のプレイヤー: {'水色' if game.current_player == 1 else 'ピンク'}")
    print()
    
    # 合法手を取得
    legal_moves = game.get_legal_moves()
    print(f"✓ 合法手の数: {len(legal_moves)}")
    
    if len(legal_moves) > 0:
        print(f"  最初の5手:")
        for i, move in enumerate(legal_moves[:5]):
            print(f"    {i+1}. {move}")
    print()
    
    # 手を適用
    if len(legal_moves) > 0:
        first_move = legal_moves[0]
        print(f"✓ 手を適用: {first_move}")
        success = game.apply_move(first_move)
        print(f"  結果: {'成功' if success else '失敗'}")
        print(f"  現在のプレイヤー: {'水色' if game.current_player == 1 else 'ピンク'}")
        print(f"  手数: {len(game.move_history)}")
        print()
    
    # 盤面の状態を確認
    info = game.get_game_info()
    print(f"✓ ゲーム情報:")
    print(f"  手数: {info['move_count']}")
    print(f"  水色ブロック: 4マス={info['player_blocks']['1']['size4']}, 5マス={info['player_blocks']['1']['size5']}")
    print(f"  ピンクブロック: 4マス={info['player_blocks']['-1']['size4']}, 5マス={info['player_blocks']['-1']['size5']}")
    print(f"  ゲーム終了: {info['is_game_over']}")
    print()
    
    # 2手目を適用
    legal_moves = game.get_legal_moves()
    if len(legal_moves) > 0:
        second_move = legal_moves[0]
        print(f"✓ 2手目を適用: {second_move}")
        success = game.apply_move(second_move)
        print(f"  結果: {'成功' if success else '失敗'}")
        print(f"  手数: {len(game.move_history)}")
        print()
    
    # 棋譜をエクスポート
    record = game.export_game_record()
    print(f"✓ 棋譜エクスポート:")
    print(f"  長さ: {len(record)} 文字")
    print()
    
    # 取り消し機能のテスト
    print(f"✓ 取り消し機能テスト:")
    print(f"  取り消し前の手数: {len(game.move_history)}")
    undo_success = game.undo_last_move()
    print(f"  取り消し結果: {'成功' if undo_success else '失敗'}")
    print(f"  取り消し後の手数: {len(game.move_history)}")
    print()
    
    # クローン機能のテスト
    cloned_game = game.clone()
    print(f"✓ クローン機能テスト:")
    print(f"  元のゲーム手数: {len(game.move_history)}")
    print(f"  クローンの手数: {len(cloned_game.move_history)}")
    print()
    
    print("=== テスト完了 ===")


def test_specific_move():
    """特定の手のテスト"""
    print("\n=== 特定の手のテスト ===\n")
    
    game = WataruToGame(board_size=18)
    
    # 水色プレイヤーが (0, 0) から横に3マス配置
    try:
        move = Move(
            player=1,
            path=[
                Position(row=0, col=0, layer=0),
                Position(row=0, col=1, layer=0),
                Position(row=0, col=2, layer=0),
            ],
            timestamp=0.0
        )
        
        print(f"✓ 手を作成: {move}")
        
        is_valid, error_msg = game.is_valid_move(move)
        print(f"  妥当性: {'有効' if is_valid else f'無効 - {error_msg}'}")
        
        if is_valid:
            success = game.apply_move(move)
            print(f"  適用結果: {'成功' if success else '失敗'}")
            
            # 盤面を確認
            for col in range(3):
                cell = game.board.get_cell(0, col)
                print(f"  (0, {col}): {cell}")
        
        print()
    except Exception as e:
        print(f"✗ エラー: {e}\n")


def test_bridge_detection():
    """橋の検出テスト"""
    print("\n=== 橋の検出テスト ===\n")
    
    game = WataruToGame(board_size=5)  # 小さい盤面でテスト
    
    # 水色が上から下まで一直線に配置
    print("✓ 水色が縦に橋を作る:")
    for row in range(5):
        game.board.set_cell(row, 2, 0, 1)  # 水色を配置
        print(f"  ({row}, 2) に水色を配置")
    
    has_bridge = game.board.check_bridge(1)
    print(f"  橋の検出: {'あり' if has_bridge else 'なし'}")
    print()
    
    # リセット
    game.board.reset()
    
    # ピンクが左から右まで一直線に配置
    print("✓ ピンクが横に橋を作る:")
    for col in range(5):
        game.board.set_cell(2, col, 0, -1)  # ピンクを配置
        print(f"  (2, {col}) にピンクを配置")
    
    has_bridge = game.board.check_bridge(-1)
    print(f"  橋の検出: {'あり' if has_bridge else 'なし'}")
    print()


if __name__ == "__main__":
    test_basic_game()
    test_specific_move()
    test_bridge_detection()
    
    print("\n✅ すべてのテストが完了しました！")

