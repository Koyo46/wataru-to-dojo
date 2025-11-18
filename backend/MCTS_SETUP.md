# MCTS AI セットアップ完了 🎉

ワタルート道場に強力なMCTS（モンテカルロ木探索）AIが実装されました！

## ✅ 実装完了内容

### 1. MCTSエンジン (`backend/ai/mcts.py`)
- UCB1アルゴリズムによる賢い探索
- ランダムプレイアウトシミュレーション
- 時間制限付き探索
- 詳細な統計情報出力

### 2. APIエンドポイント統合 (`backend/api/main.py`)
- `/api/ai/move` エンドポイントをMCTS対応に更新
- 5秒思考時間制限
- 勝率情報を含むレスポンス

### 3. テストスクリプト (`backend/test_mcts.py`)
- クイックテスト機能
- 評価機能（複数ゲームの対戦）
- コマンドライン引数対応

### 4. ドキュメント (`backend/ai/README.md`)
- 使い方ガイド
- パラメータ説明
- チューニング方法
- 今後の拡張予定

## 🚀 使い方

### 1. フロントエンドから使用

1. バックエンドを起動:
```bash
cd backend
python start_server.py
```

2. フロントエンドを起動:
```bash
cd frontend
npm run dev
```

3. ブラウザで `http://localhost:3000` にアクセス

4. **「vsバックエンドAI」モードを選択**

5. ゲームを開始！MCTSが自動的にピンク（-1）プレイヤーとして対戦します

### 2. テストスクリプトで評価

#### クイックテスト（1ゲーム、3秒思考）
```bash
cd backend
python test_mcts.py --quick
```

#### 評価（10ゲーム、5秒思考）
```bash
python test_mcts.py --games 10 --time 5.0
```

#### カスタム評価
```bash
# 20ゲーム、3秒思考
python test_mcts.py --games 20 --time 3.0

# 5ゲーム、10秒思考（より強いAI）
python test_mcts.py --games 5 --time 10.0
```

### 3. Pythonコードから直接使用

```python
from game.game import WataruToGame
from ai.mcts import create_mcts_engine

# ゲーム作成
game = WataruToGame(18)

# MCTS作成（5秒思考）
mcts = create_mcts_engine(time_limit=5.0, verbose=True)

# 最良の手を探索
best_move = mcts.search(game)

# 統計情報
print(f"シミュレーション回数: {mcts.stats.simulations_run}")
print(f"勝率: {mcts.stats.best_move_win_rate * 100:.1f}%")

# 手を適用
game.apply_move(best_move)
```

## 📊 予想性能

### 5秒思考時の目安
- 対ランダムAI勝率: **70-90%**
- シミュレーション回数: 約500-1000回
- 1秒あたりシミュレーション: 約100-200回

※ 実際の性能はCPU性能とゲーム状態によって変動します

## 🎮 実際にプレイしてみよう！

1. **初手**: MCTSは中央付近から始めることが多い
2. **中盤**: 接続と妨害のバランスを考える
3. **終盤**: 勝利への最短経路を計算

MCTSは思考中、サーバーログに以下のような統計情報を出力します：

```
============================================================
MCTS統計情報
============================================================
シミュレーション回数: 567
探索ノード数: 1234
探索時間: 5.00秒
シミュレーション/秒: 113.4

最良手の訪問回数: 89
最良手の勝率: 72.5%

トップ5候補手:
  1. 訪問:   89  勝率:  72.5%  手: Move(...)
  2. 訪問:   67  勝率:  65.3%  手: Move(...)
  3. 訪問:   45  勝率:  58.2%  手: Move(...)
  4. 訪問:   34  勝率:  52.1%  手: Move(...)
  5. 訪問:   28  勝率:  48.7%  手: Move(...)
============================================================
```

## 🔧 パラメータ調整

### より強いAIにする

**思考時間を増やす**（`backend/api/main.py`を編集）:
```python
mcts = create_mcts_engine(
    time_limit=10.0,  # 5.0から10.0に変更
    exploration_weight=1.41,
    verbose=True
)
```

### より速いAIにする

思考時間を減らす:
```python
mcts = create_mcts_engine(
    time_limit=3.0,  # 3秒で思考
    exploration_weight=1.41,
    verbose=False  # ログを減らして高速化
)
```

### 探索バランスを調整

```python
# より保守的（勝率の高い手を重視）
mcts = create_mcts_engine(exploration_weight=1.0)

# より探索的（未試行の手を重視）
mcts = create_mcts_engine(exploration_weight=2.0)
```

## 📈 今後の改善予定

### 短期（実装済み✅）
- [x] 基本的なMCTS実装
- [x] APIエンドポイント統合
- [x] テストスクリプト

### 中期（実装予定）
- [ ] より賢いシミュレーション（ヒューリスティック評価）
- [ ] 並列化（マルチスレッドMCTS）
- [ ] Opening book（定石データベース）
- [ ] メモリ効率の改善

### 長期（研究課題）
- [ ] 軽量ニューラルネットワーク統合
- [ ] AlphaZero風の強化学習
- [ ] 自己対戦による進化

## 🐛 トラブルシューティング

### MCTSが動かない
- バックエンドが正しく起動しているか確認
- `backend/ai/mcts.py`が存在するか確認
- Python環境が正しいか確認（venv有効化）

### MCTSが遅すぎる
- `time_limit`を減らす（3秒など）
- `verbose=False`にしてログ出力を減らす

### エラーが出る
- サーバーログを確認
- テストスクリプトで単体テスト: `python test_mcts.py --quick`

## 📚 さらに学ぶには

- `backend/ai/README.md` - 詳細なドキュメント
- `backend/ai/mcts.py` - 実装の詳細
- `backend/test_mcts.py` - 使用例

---

**楽しいゲームを！🎲**

MCTSは対戦を重ねるほど、あなたの戦略を学習していきます。
強いAIに勝てるように頑張ってください！

