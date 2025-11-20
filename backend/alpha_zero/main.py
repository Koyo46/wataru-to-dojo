"""
Alpha Zero 学習メインスクリプト

ワタルートゲームでAlpha Zero方式の強化学習を実行
"""

import os
import sys

# 再帰深度制限を増やす（MCTSの深い探索用）
sys.setrecursionlimit(10000)

# alpha-zero-generalをパスに追加
alpha_zero_general_path = os.path.join(os.path.dirname(__file__), '..', 'alpha-zero-general')
sys.path.append(alpha_zero_general_path)

# 現在のディレクトリをパスに追加（同じディレクトリのモジュールをインポート可能にする）
sys.path.insert(0, os.path.dirname(__file__))

# 深さ制限付きCoachを使用
from DepthLimitedCoach import DepthLimitedCoach as Coach
from WataruToGame import WataruToGame
from pytorch.NNet import NNetWrapper as nn
from utils import dotdict


def main():
    """
    学習のメイン処理
    
    フェーズ1: プロトタイプ（動作確認）
    フェーズ2: 短期学習（性能評価）
    フェーズ3: 本格学習（強いAI）
    """
    
    print("=" * 70)
    print("Alpha Zero - ワタルート学習")
    print("=" * 70)
    
    # ========== 設定 ==========
    
    # ゲーム設定
    BOARD_SIZE = 9  # 9x9盤面から開始
    
    # 学習フェーズの選択
    print("\n学習フェーズを選択してください:")
    print("  1. プロトタイプ（3イテレーション、約30分-1時間）")
    print("  2. 短期学習（20イテレーション、約3-4時間）")
    print("  3. 本格学習（100イテレーション、約1-2日）")
    print("  4. カスタム設定")
    
    # 環境変数があればそれを使用、なければユーザー入力
    if 'ALPHA_ZERO_MODE' in os.environ:
        choice = os.environ.get('ALPHA_ZERO_MODE', '1').strip()
        print(f"\n選択: {choice} (環境変数 ALPHA_ZERO_MODE)")
    else:
        choice = input("\n選択 (1-4): ").strip()
        if choice not in ['1', '2', '3', '4']:
            print("無効な選択です。プロトタイプモード (1) を使用します。")
            choice = '1'
    
    if choice == '1':
        # フェーズ1: プロトタイプ（既存モデルに合わせて96ch/6blocks）
        args = dotdict({
            'numIters': 3,              # イテレーション数（5→3に削減）
            'numEps': 5,                # 各イテレーションの自己対戦数（10→5に削減）
            'tempThreshold': 15,        # 温度パラメータの閾値
            'updateThreshold': 0.55,    # モデル更新の勝率閾値
            'maxlenOfQueue': 5000,      # 経験再生バッファサイズ
            'numMCTSSims': 25,          # MCTSシミュレーション回数（50→25に削減）
            'arenaCompare': 5,          # モデル評価の対戦回数（10→5に削減）
            'cpuct': 1.0,               # MCTS探索パラメータ
            'max_depth': 30,            # ★新機能: MCTS最大探索深さ
            
            # ニューラルネット設定（既存モデルと一致させる）
            'lr': 0.001,
            'dropout': 0.3,
            'epochs': 3,                # エポック数も削減（5→3）
            'batch_size': 32,
            'num_channels': 96,         # 既存モデルに合わせる（64→96）
            'num_res_blocks': 6,        # 既存モデルに合わせる（4→6）
            
            # その他
            'checkpoint': './models/',
            'load_model': False,
            'load_folder_file': ('./models/', 'best.pth.tar'),
            'numItersForTrainExamplesHistory': 3,
        })
        print("\n✅ プロトタイプモード（動作確認、深さ制限付き）")
    
    elif choice == '2':
        # フェーズ2: 短期学習
        args = dotdict({
            'numIters': 20,
            'numEps': 15,
            'tempThreshold': 15,
            'updateThreshold': 0.55,
            'maxlenOfQueue': 10000,
            'numMCTSSims': 75,
            'arenaCompare': 15,
            'cpuct': 1.0,
            'max_depth': 40,            # ★追加: MCTS最大探索深さ
            
            'lr': 0.001,
            'dropout': 0.3,
            'epochs': 8,
            'batch_size': 64,
            'num_channels': 96,
            'num_res_blocks': 6,
            
            'checkpoint': './models/',
            'load_model': False,
            'load_folder_file': ('./models/', 'best.pth.tar'),
            'numItersForTrainExamplesHistory': 15,
        })
        print("\n✅ 短期学習モード（性能評価）")
    
    elif choice == '3':
        # フェーズ3: 本格学習
        args = dotdict({
            'numIters': 100,
            'numEps': 25,
            'tempThreshold': 15,
            'updateThreshold': 0.55,
            'maxlenOfQueue': 20000,
            'numMCTSSims': 100,
            'arenaCompare': 20,
            'cpuct': 1.0,
            'max_depth': 50,            # ★追加: MCTS最大探索深さ
            
            'lr': 0.001,
            'dropout': 0.3,
            'epochs': 10,
            'batch_size': 64,
            'num_channels': 128,
            'num_res_blocks': 8,
            
            'checkpoint': './models/',
            'load_model': False,
            'load_folder_file': ('./models/', 'best.pth.tar'),
            'numItersForTrainExamplesHistory': 20,
        })
        print("\n✅ 本格学習モード（強いAI）")
    
    else:
        # カスタム設定
        print("\nカスタム設定を入力してください:")
        num_iters = int(input("イテレーション数 (デフォルト: 10): ") or "10")
        num_eps = int(input("各イテレーションの対戦数 (デフォルト: 15): ") or "15")
        num_sims = int(input("MCTSシミュレーション回数 (デフォルト: 75): ") or "75")
        
        args = dotdict({
            'numIters': num_iters,
            'numEps': num_eps,
            'tempThreshold': 15,
            'updateThreshold': 0.55,
            'maxlenOfQueue': 10000,
            'numMCTSSims': num_sims,
            'arenaCompare': 15,
            'cpuct': 1.0,
            'max_depth': 40,            # ★追加: MCTS最大探索深さ
            
            'lr': 0.001,
            'dropout': 0.3,
            'epochs': 8,
            'batch_size': 64,
            'num_channels': 96,
            'num_res_blocks': 6,
            
            'checkpoint': './models/',
            'load_model': False,
            'load_folder_file': ('./models/', 'best.pth.tar'),
            'numItersForTrainExamplesHistory': 15,
        })
        print("\n✅ カスタムモード")
    
    # モデル再開の確認
    if os.path.exists(os.path.join(args.checkpoint, 'best.pth.tar')):
        resume = input("\n既存のモデルが見つかりました。続きから学習しますか？ (y/n): ").strip().lower()
        if resume == 'y':
            args.load_model = True
            print("✅ 学習済みモデルから再開します")
    
    # ========== 学習開始 ==========
    
    print("\n" + "=" * 70)
    print("設定サマリー")
    print("=" * 70)
    print(f"盤面サイズ: {BOARD_SIZE}x{BOARD_SIZE}")
    print(f"イテレーション数: {args.numIters}")
    print(f"各イテレーションの対戦数: {args.numEps}")
    print(f"MCTSシミュレーション回数: {args.numMCTSSims}")
    print(f"バッチサイズ: {args.batch_size}")
    print(f"ニューラルネット:")
    print(f"  - チャンネル数: {args.num_channels}")
    print(f"  - 残差ブロック数: {args.num_res_blocks}")
    print(f"  - エポック数: {args.epochs}")
    print(f"モデル保存先: {args.checkpoint}")
    print("=" * 70)
    
    # 確認
    confirm = input("\nこの設定で学習を開始しますか？ (y/n): ").strip().lower()
    if confirm != 'y':
        print("学習をキャンセルしました")
        return
    
    print("\n🚀 学習開始！\n")
    
    # ゲームとニューラルネットの作成
    game = WataruToGame(board_size=BOARD_SIZE)
    nnet = nn(game, args)
    
    # 学習済みモデルの読み込み（オプション）
    if args.load_model:
        # モデルの互換性を事前チェック
        checkpoint_path = os.path.join(args.checkpoint, 'best.pth.tar')
        if os.path.exists(checkpoint_path):
            try:
                import torch
                checkpoint = torch.load(checkpoint_path, map_location='cpu')
                
                # チェックポイントからネットワーク構造情報を取得
                saved_channels = checkpoint.get('num_channels', None)
                saved_res_blocks = checkpoint.get('num_res_blocks', None)
                
                # 既存モデルの構造が記録されている場合、それに合わせる
                if saved_channels is not None and saved_res_blocks is not None:
                    if saved_channels != args.num_channels or saved_res_blocks != args.num_res_blocks:
                        print(f"\n既存モデルの構造を検出:")
                        print(f"   既存: チャンネル={saved_channels}, 残差ブロック={saved_res_blocks}")
                        print(f"   選択した設定: チャンネル={args.num_channels}, 残差ブロック={args.num_res_blocks}")
                        print(f"\n既存モデルから学習を続けるため、ネットワーク構造を既存モデルに合わせます。")
                        
                        # ネットワーク構造を既存モデルに合わせる
                        args.num_channels = saved_channels
                        args.num_res_blocks = saved_res_blocks
                        
                        print(f"✅ 設定を変更: チャンネル={args.num_channels}, 残差ブロック={args.num_res_blocks}\n")
                        
                        # ネットワークを再作成
                        nnet = nn(game, args)
            except Exception as e:
                print(f"モデル情報の読み込み中にエラー: {e}")
                print("新規学習として開始します\n")
                args.load_model = False
        
        # モデルのロード
        if args.load_model:
            try:
                nnet.load_checkpoint(args.checkpoint, 'best.pth.tar')
                print("✅ 学習済みモデル読み込み完了\n")
            except Exception as e:
                print(f"⚠️ モデル読み込み失敗: {e}")
                print("新規学習を開始します\n")
                args.load_model = False
    
    # Coachの作成
    c = Coach(game, nnet, args)
    
    # 学習例の読み込み（再開時）
    if args.load_model:
        print("以前の学習例を読み込んでいます...")
        try:
            c.loadTrainExamples()
            print("✅ 学習例読み込み完了\n")
        except Exception as e:
            print(f"⚠️ 学習例読み込み失敗: {e}\n")
    
    # 学習ループ
    try:
        c.learn()
    except KeyboardInterrupt:
        print("\n\n⚠️ 学習が中断されました")
        print("モデルは自動保存されています")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("学習完了")
    print("=" * 70)
    print(f"最終モデル: {args.checkpoint}best.pth.tar")
    print("このモデルを使ってゲームと対戦できます！")


if __name__ == "__main__":
    main()

