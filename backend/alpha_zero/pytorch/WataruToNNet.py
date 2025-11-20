"""
ワタルート用ニューラルネットワーク（PyTorch実装）

ResNet風のアーキテクチャでAlpha Zero方式の学習を実現
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ResNetBlock(nn.Module):
    """
    残差ブロック（Residual Block）
    
    AlphaGoやAlphaZeroで使用される基本的な構造
    勾配消失問題を防ぎ、深いネットワークの学習を可能にする
    """
    
    def __init__(self, num_channels: int):
        """
        Args:
            num_channels: チャンネル数
        """
        super(ResNetBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(num_channels, num_channels, 3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(num_channels)
        
        self.conv2 = nn.Conv2d(num_channels, num_channels, 3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(num_channels)
    
    def forward(self, x):
        """
        順伝播
        
        x -> conv1 -> bn1 -> relu -> conv2 -> bn2 -> (+x) -> relu
        """
        residual = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = F.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        # スキップ接続（残差接続）
        out += residual
        out = F.relu(out)
        
        return out


class WataruToNNet(nn.Module):
    """
    ワタルート用ニューラルネットワーク
    
    入力: 盤面の状態 (6チャンネル × board_size × board_size)
          - チャンネル0-3: 盤面（P1層1, P1層2, P-1層1, P-1層2）
          - チャンネル4-5: 残りブロック情報（P1, P-1）
    
    出力1: 方策（Policy）- 各手の確率分布
    出力2: 価値（Value）- 現在の局面評価 (-1.0 ~ 1.0)
    """
    
    def __init__(
        self, 
        game, 
        num_channels: int = 128,
        num_res_blocks: int = 8,
        dropout: float = 0.3
    ):
        """
        Args:
            game: WataruToGameオブジェクト
            num_channels: 畳み込み層のチャンネル数（GTX 1650では128推奨）
            num_res_blocks: 残差ブロックの数（GTX 1650では8推奨）
            dropout: ドロップアウト率
        """
        super(WataruToNNet, self).__init__()
        
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.num_channels = num_channels
        
        # 入力チャンネル: 盤面4 + 残りブロック2 = 6
        self.input_channels = 6
        
        # ========== 共有部分 ==========
        # 最初の畳み込み層
        self.conv_input = nn.Conv2d(
            self.input_channels, 
            num_channels, 
            3, 
            stride=1, 
            padding=1
        )
        self.bn_input = nn.BatchNorm2d(num_channels)
        
        # 残差ブロック
        self.res_blocks = nn.ModuleList([
            ResNetBlock(num_channels) 
            for _ in range(num_res_blocks)
        ])
        
        # ========== 方策ヘッド（Policy Head）==========
        # 各手の確率を出力
        self.conv_policy = nn.Conv2d(num_channels, 16, 1)  # 1x1畳み込みで次元削減
        self.bn_policy = nn.BatchNorm2d(16)
        self.fc_policy = nn.Linear(
            16 * self.board_x * self.board_y, 
            self.action_size
        )
        
        # ========== 価値ヘッド（Value Head）==========
        # 局面の評価値を出力
        self.conv_value = nn.Conv2d(num_channels, 16, 1)
        self.bn_value = nn.BatchNorm2d(16)
        self.fc_value1 = nn.Linear(
            16 * self.board_x * self.board_y, 
            128
        )
        self.fc_value2 = nn.Linear(128, 1)
        
        # ドロップアウト
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, s):
        """
        順伝播
        
        Args:
            s: 盤面の状態テンソル
               形状: (batch_size, 6, board_size, board_size)
        
        Returns:
            pi: 方策（log確率）
                形状: (batch_size, action_size)
            v: 価値
               形状: (batch_size, 1)
        """
        # 入力: (batch, 6, board_size, board_size)
        s = s.view(-1, self.input_channels, self.board_x, self.board_y)
        
        # 最初の畳み込み
        s = F.relu(self.bn_input(self.conv_input(s)))
        
        # 残差ブロックを通過
        for res_block in self.res_blocks:
            s = res_block(s)
        
        # ========== 方策ヘッド ==========
        pi = F.relu(self.bn_policy(self.conv_policy(s)))
        pi = pi.view(-1, 16 * self.board_x * self.board_y)
        pi = self.dropout(pi)
        pi = self.fc_policy(pi)
        
        # ========== 価値ヘッド ==========
        v = F.relu(self.bn_value(self.conv_value(s)))
        v = v.view(-1, 16 * self.board_x * self.board_y)
        v = self.dropout(v)
        v = F.relu(self.fc_value1(v))
        v = self.fc_value2(v)
        
        # 方策はlog_softmax、価値はtanhで正規化
        return F.log_softmax(pi, dim=1), torch.tanh(v)


def test_network():
    """ネットワークの動作テスト"""
    print("=" * 60)
    print("WataruToNNet テスト")
    print("=" * 60)
    
    # ダミーのゲームオブジェクト
    class DummyGame:
        def getBoardSize(self):
            return (9, 9)
        def getActionSize(self):
            return 4 * 9 * 9  # 324
    
    game = DummyGame()
    
    # ネットワーク作成
    print("\nネットワーク作成中...")
    nnet = WataruToNNet(game, num_channels=128, num_res_blocks=8)
    
    # パラメータ数を計算
    total_params = sum(p.numel() for p in nnet.parameters())
    trainable_params = sum(p.numel() for p in nnet.parameters() if p.requires_grad)
    
    print(f"総パラメータ数: {total_params:,}")
    print(f"学習可能パラメータ数: {trainable_params:,}")
    print(f"モデルサイズ: {total_params * 4 / 1024 / 1024:.2f} MB (float32)")
    
    # テスト入力
    print("\nテスト実行中...")
    batch_size = 8
    test_input = torch.randn(batch_size, 6, 9, 9)
    
    # 順伝播
    with torch.no_grad():
        pi, v = nnet(test_input)
    
    print(f"\n入力形状: {test_input.shape}")
    print(f"方策出力形状: {pi.shape}")
    print(f"価値出力形状: {v.shape}")
    
    # 方策の確率への変換
    probs = torch.exp(pi)
    print(f"\n方策の合計（各バッチ）: {probs.sum(dim=1)}")
    print(f"価値の範囲: [{v.min().item():.3f}, {v.max().item():.3f}]")
    
    # CUDA対応テスト
    if torch.cuda.is_available():
        print("\n" + "=" * 60)
        print("CUDA テスト")
        print("=" * 60)
        
        nnet_cuda = nnet.cuda()
        test_input_cuda = test_input.cuda()
        
        with torch.no_grad():
            pi_cuda, v_cuda = nnet_cuda(test_input_cuda)
        
        print("✅ CUDAで正常動作")
        print(f"GPU使用メモリ: {torch.cuda.memory_allocated() / 1024 / 1024:.2f} MB")
    
    print("\n✅ テスト完了！")


if __name__ == "__main__":
    test_network()

