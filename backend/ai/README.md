# ワタルート道場 AI 実装

このディレクトリには、ワタルートゲームの強力なAI実装が含まれています。

## 🤖 実装済みAI

### MCTS (モンテカルロ木探索)

**ファイル**: `mcts.py`

ワタルート用の高性能MCTSエンジン。UCB1アルゴリズムを使用して最適な手を探索します。

#### 特徴
- UCB1による賢い選択
- ランダムプレイアウトによるシミュレーション
- 時間制限とシミュレーション回数制限に対応
- 詳細な統計情報出力

#### パラメータ
- `time_limit`: 探索時間制限（秒）デフォルト: 5.0
- `exploration_weight`: 探索の重み（通常は√2）デフォルト: 1.41
- `max_simulations`: 最大シミュレーション回数（Noneなら時間制限のみ）
- `verbose`: 詳細な統計情報を出力するか

## 📖 使い方

### 基本的な使用例

```python
from game.game import WataruToGame
from ai.mcts import create_mcts_engine

# ゲームを作成
game = WataruToGame(18)

# MCTSエンジンを作成（5秒思考）
mcts = create_mcts_engine(time_limit=5.0, verbose=True)

# 最良の手を探索
best_move = mcts.search(game)

# 手を適用
game.apply_move(best_move)

# 統計情報を確認
print(f"シミュレーション回数: {mcts.stats.simulations_run}")
print(f"勝率: {mcts.stats.best_move_win_rate * 100:.1f}%")
```

### APIエンドポイント

MCTSは既にバックエンドAPIに統合されています：

```
POST /api/ai/move
```

リクエスト:
```json
{
  "game_id": "your-game-id",
  "player": -1
}
```

レスポンス:
```json
{
  "game_id": "your-game-id",
  "move": {
    "player": -1,
    "path": [...],
    "timestamp": 1234567890.0
  },
  "message": "MCTS AI move (勝率: 75.3%)"
}
```

## 🧪 テスト

### クイックテスト（1ゲーム）

```bash
cd backend
python test_mcts.py --quick
```

### 評価（複数ゲーム）

```bash
# 10ゲーム、5秒思考
python test_mcts.py --games 10 --time 5.0

# 20ゲーム、3秒思考
python test_mcts.py --games 20 --time 3.0
```

## 📊 性能

現在の設定（5秒思考）での目安：

- **対ランダムAI勝率**: 70-90%
- **1秒あたりシミュレーション**: 約100-200回
- **平均探索ノード数**: 数百〜数千ノード

※ 実際の性能はハードウェアやゲーム状態によって変動します

## 🔧 チューニング

### より強いAIにする方法

1. **思考時間を増やす**
   ```python
   mcts = create_mcts_engine(time_limit=10.0)  # 10秒思考
   ```

2. **探索パラメータを調整**
   ```python
   # より保守的（exploitation重視）
   mcts = create_mcts_engine(exploration_weight=1.0)
   
   # より探索的（exploration重視）
   mcts = create_mcts_engine(exploration_weight=2.0)
   ```

3. **シミュレーションを改善**
   - 現在はランダムプレイアウトですが、ヒューリスティックな評価関数を追加可能
   - `_simulate_random_playout`メソッドを拡張

## 🚀 今後の拡張予定

### 短期的な改善
- [ ] より賢いプレイアウト（ヒューリスティック評価）
- [ ] 並列化（マルチスレッド）
- [ ] メモリ効率の改善

### 中期的な改善
- [ ] 軽量ニューラルネットワークとの統合
- [ ] 評価関数の追加（接続性評価など）
- [ ] Opening book（定石データベース）

### 長期的な目標
- [ ] AlphaZero風の強化学習
- [ ] 深層ニューラルネットワーク統合
- [ ] 自己対戦による学習システム

## 📝 アルゴリズム詳細

### MCTS の4ステップ

1. **Selection（選択）**: UCB1スコアで最良の子ノードを選択
2. **Expansion（展開）**: 新しい子ノードを作成
3. **Simulation（シミュレーション）**: ゲーム終了までランダムプレイアウト
4. **Backpropagation（逆伝播）**: 結果を親ノードに伝播

### UCB1計算式

```
UCB1 = (wins / visits) + C × √(ln(parent_visits) / visits)
```

- 第1項: 利用（exploitation）- 勝率の高い手を選ぶ
- 第2項: 探索（exploration）- まだ試していない手を試す
- C: 探索の重み（通常は√2 ≈ 1.41）

## 🐛 トラブルシューティング

### MCTSが遅い

- `time_limit`を減らす
- 盤面サイズを小さくする（テスト用）
- 並列化を検討

### メモリ不足

- `time_limit`を減らしてノード数を抑える
- ゲーム状態のコピーを最適化

### 勝率が低い

- `time_limit`を増やす
- `exploration_weight`を調整
- シミュレーションの質を改善

## 📚 参考文献

- [Monte Carlo Tree Search - Wikipedia](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
- [UCB1 Algorithm](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search#Exploration_and_exploitation)
- [AlphaGo論文](https://www.nature.com/articles/nature16961)

## 🤝 貢献

AIの改善アイデアや実装があれば、ぜひ貢献してください！

---

**作成日**: 2025-11-18
**バージョン**: 1.0.0

