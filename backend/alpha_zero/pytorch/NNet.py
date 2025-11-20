"""
ニューラルネットワークラッパー - 学習・推論インターフェース

alpha-zero-generalのNeuralNet抽象クラスに準拠した実装
"""

import os
import sys
import time
import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from alpha_zero.pytorch.WataruToNNet import WataruToNNet


class WataruToDataset(Dataset):
    """
    学習データセット
    
    自己対戦で得られたデータを効率的にバッチ処理
    """
    
    def __init__(self, examples):
        """
        Args:
            examples: [(board, pi, v), ...] のリスト
        """
        self.examples = examples
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        board, pi, v = self.examples[idx]
        return board, pi, v


class NNetWrapper:
    """
    ニューラルネットワークのラッパークラス
    
    学習・推論・モデル保存/読込の機能を提供
    """
    
    def __init__(self, game, args=None):
        """
        Args:
            game: WataruToGameオブジェクト
            args: ハイパーパラメータを含む辞書
        """
        self.game = game
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        
        # デフォルト引数
        default_args = {
            'lr': 0.001,
            'dropout': 0.3,
            'epochs': 10,
            'batch_size': 64,
            'cuda': torch.cuda.is_available(),
            'num_channels': 128,
            'num_res_blocks': 8,
        }
        
        self.args = {**default_args, **(args or {})}
        
        # ネットワークの作成
        self.nnet = WataruToNNet(
            game,
            num_channels=self.args['num_channels'],
            num_res_blocks=self.args['num_res_blocks'],
            dropout=self.args['dropout']
        )
        
        # CUDA対応
        if self.args['cuda']:
            self.nnet.cuda()
        
        print(f"ニューラルネットワーク作成完了")
        print(f"  デバイス: {'CUDA' if self.args['cuda'] else 'CPU'}")
        print(f"  チャンネル数: {self.args['num_channels']}")
        print(f"  残差ブロック数: {self.args['num_res_blocks']}")
        
        # パラメータ数の表示
        total_params = sum(p.numel() for p in self.nnet.parameters())
        print(f"  総パラメータ数: {total_params:,}")
    
    def train(self, examples):
        """
        自己対戦データで学習
        
        Args:
            examples: [(board, pi, v), ...] のリスト
                     board: 盤面状態
                     pi: MCTS探索結果（方策）
                     v: 最終的な勝敗（価値）
        """
        optimizer = optim.Adam(self.nnet.parameters(), lr=self.args['lr'])
        
        print(f"\n学習開始: {len(examples)}例")
        
        # デバッグ: 最初のサンプルをチェック
        if len(examples) > 0:
            sample_board, sample_pi, sample_v = examples[0]
            print(f"デバッグ: サンプルデータの形状:")
            print(f"  board type: {type(sample_board)}, shape: {np.array(sample_board).shape if isinstance(sample_board, (list, np.ndarray)) else 'N/A'}")
            print(f"  pi type: {type(sample_pi)}, length: {len(sample_pi) if hasattr(sample_pi, '__len__') else 'N/A'}")
            print(f"  v type: {type(sample_v)}, value: {sample_v}")
            print(f"  期待されるアクション数: {self.action_size}")
        
        # カスタムcollate関数（データの形状を保証）
        def custom_collate(batch):
            boards = [item[0] for item in batch]
            pis = [item[1] for item in batch]
            vs = [item[2] for item in batch]
            return boards, pis, vs
        
        # データセットとローダーの作成
        dataset = WataruToDataset(examples)
        dataloader = DataLoader(
            dataset,
            batch_size=self.args['batch_size'],
            shuffle=True,
            num_workers=0,  # Windowsでは0推奨
            collate_fn=custom_collate  # カスタムcollate関数を使用
        )
        
        self.nnet.train()
        
        for epoch in range(self.args['epochs']):
            print(f"\nエポック {epoch + 1}/{self.args['epochs']}")
            
            batch_count = 0
            pi_losses = []
            v_losses = []
            total_losses = []
            
            epoch_start = time.time()
            
            for batch_idx, (boards, target_pis, target_vs) in enumerate(dataloader):
                # データをテンソルに変換
                boards = torch.FloatTensor(np.array(boards))
                target_pis = torch.FloatTensor(np.array(target_pis))
                target_vs = torch.FloatTensor(np.array(target_vs))
                
                # デバッグ: サイズチェック（最初のバッチのみ）
                if batch_idx == 0 and epoch == 0:
                    print(f"\nデバッグ情報:")
                    print(f"  boards shape: {boards.shape}")
                    print(f"  target_pis shape: {target_pis.shape}")
                    print(f"  target_vs shape: {target_vs.shape}")
                    print(f"  期待されるアクション数: {self.action_size}")
                
                # CUDA対応
                if self.args['cuda']:
                    boards = boards.cuda()
                    target_pis = target_pis.cuda()
                    target_vs = target_vs.cuda()
                
                # 順伝播
                out_pi, out_v = self.nnet(boards)
                
                # デバッグ: 出力サイズチェック（最初のバッチのみ）
                if batch_idx == 0 and epoch == 0:
                    print(f"  out_pi shape: {out_pi.shape}")
                    print(f"  out_v shape: {out_v.shape}")
                
                # 損失計算
                l_pi = self.loss_pi(target_pis, out_pi)
                l_v = self.loss_v(target_vs, out_v)
                total_loss = l_pi + l_v
                
                # 記録
                pi_losses.append(l_pi.item())
                v_losses.append(l_v.item())
                total_losses.append(total_loss.item())
                
                # 逆伝播
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()
                
                batch_count += 1
            
            epoch_time = time.time() - epoch_start
            
            # エポック結果の表示
            print(f"  時間: {epoch_time:.2f}秒")
            print(f"  方策損失: {np.mean(pi_losses):.4f}")
            print(f"  価値損失: {np.mean(v_losses):.4f}")
            print(f"  合計損失: {np.mean(total_losses):.4f}")
            print(f"  バッチ数: {batch_count}")
        
        print("\n✅ 学習完了")
    
    def predict(self, board):
        """
        盤面の評価
        
        Args:
            board: WataruToGameオブジェクト
        
        Returns:
            pi: 方策（確率分布）- numpy配列
            v: 価値（スカラー）- float
        """
        # ボードをテンソルに変換
        board_tensor = self.board_to_tensor(board)
        board_tensor = torch.FloatTensor(board_tensor.astype(np.float32))
        
        if self.args['cuda']:
            board_tensor = board_tensor.cuda()
        
        # バッチ次元追加
        board_tensor = board_tensor.unsqueeze(0)
        
        self.nnet.eval()
        with torch.no_grad():
            pi, v = self.nnet(board_tensor)
        
        # 確率に変換（log_softmax -> softmax）
        pi = torch.exp(pi).cpu().numpy()[0]
        v = v.cpu().numpy()[0][0]
        
        return pi, v
    
    def loss_pi(self, targets, outputs):
        """
        方策の損失（クロスエントロピー）
        
        Args:
            targets: 目標方策（MCTS探索結果）
            outputs: ネットワーク出力（log確率）
        
        Returns:
            損失
        """
        return -torch.sum(targets * outputs) / targets.size(0)
    
    def loss_v(self, targets, outputs):
        """
        価値の損失（平均二乗誤差）
        
        Args:
            targets: 目標価値（実際の勝敗）
            outputs: ネットワーク出力
        
        Returns:
            損失
        """
        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size(0)
    
    def save_checkpoint(self, folder='models', filename='checkpoint.pth.tar'):
        """
        モデルの保存
        
        Args:
            folder: 保存先フォルダ
            filename: ファイル名
        """
        filepath = os.path.join(folder, filename)
        
        # フォルダが存在しない場合は作成
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # モデルの状態を保存（ネットワーク構造情報も含める）
        torch.save({
            'state_dict': self.nnet.state_dict(),
            'args': self.args,
            'num_channels': self.args.get('num_channels', 64),
            'num_res_blocks': self.args.get('num_res_blocks', 4),
        }, filepath)
        
        print(f"✅ モデル保存: {filepath}")
    
    def load_checkpoint(self, folder='models', filename='checkpoint.pth.tar'):
        """
        モデルの読み込み
        
        Args:
            folder: 読み込み元フォルダ
            filename: ファイル名
        """
        filepath = os.path.join(folder, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"モデルファイルが見つかりません: {filepath}")
        
        # CPUとCUDA両対応の読み込み
        map_location = None if self.args['cuda'] else 'cpu'
        checkpoint = torch.load(filepath, map_location=map_location)
        
        self.nnet.load_state_dict(checkpoint['state_dict'])
        
        print(f"✅ モデル読み込み: {filepath}")
    
    def board_to_tensor(self, board):
        """
        盤面をテンソル形式に変換
        
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
        blocks_channel = np.zeros((2, self.board_x, self.board_y), dtype=np.float32)
        
        # プレイヤー1の残りブロック情報
        p1_blocks = board.player_blocks[1]
        blocks_channel[0, :, :] = (p1_blocks.size4 + p1_blocks.size5) / 2.0
        
        # プレイヤー-1の残りブロック情報
        p_neg1_blocks = board.player_blocks[-1]
        blocks_channel[1, :, :] = (p_neg1_blocks.size4 + p_neg1_blocks.size5) / 2.0
        
        # 結合 (6, size, size)
        full_tensor = np.concatenate([board_tensor, blocks_channel], axis=0)
        
        return full_tensor


def test_wrapper():
    """ラッパーの動作テスト"""
    print("=" * 60)
    print("NNetWrapper テスト")
    print("=" * 60)
    
    # ダミーのゲームとラッパー
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from WataruToGame import WataruToGame
    
    game = WataruToGame(board_size=9)
    args = {
        'lr': 0.001,
        'dropout': 0.3,
        'epochs': 2,
        'batch_size': 32,
        'cuda': torch.cuda.is_available(),
        'num_channels': 64,  # テスト用に小さめ
        'num_res_blocks': 4,
    }
    
    nnet = NNetWrapper(game, args)
    
    # 予測テスト
    print("\n予測テスト...")
    board = game.getInitBoard()
    pi, v = nnet.predict(board)
    
    print(f"方策の形状: {pi.shape}")
    print(f"方策の合計: {np.sum(pi):.4f}")
    print(f"価値: {v:.4f}")
    
    # 学習テスト（ダミーデータ）
    print("\n学習テスト（ダミーデータ）...")
    examples = []
    for i in range(10):
        board_tensor = nnet.board_to_tensor(board)
        pi_dummy = np.random.random(game.getActionSize())
        pi_dummy = pi_dummy / np.sum(pi_dummy)  # 正規化
        v_dummy = np.random.random() * 2 - 1  # [-1, 1]
        examples.append((board_tensor, pi_dummy, v_dummy))
    
    nnet.train(examples)
    
    # 保存/読み込みテスト
    print("\nモデル保存/読み込みテスト...")
    test_folder = 'test_models'
    nnet.save_checkpoint(folder=test_folder, filename='test.pth.tar')
    nnet.load_checkpoint(folder=test_folder, filename='test.pth.tar')
    
    # クリーンアップ
    import shutil
    if os.path.exists(test_folder):
        shutil.rmtree(test_folder)
    
    print("\n✅ テスト完了！")


if __name__ == "__main__":
    test_wrapper()

