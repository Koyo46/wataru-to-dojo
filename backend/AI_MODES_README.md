# ワタルート道場 AI モード説明書

## 🎯 2つのAIモード

このゲームには、2つの異なるAIモードが実装されています：

### 1. **Pure MCTS（簡単モード）**
- **正式名称**: Pure Monte Carlo Tree Search
- **特徴**: 完全ランダムプレイアウト
- **強さ**: ★☆☆☆☆（初心者向け）
- **速度**: ★★★★★（非常に速い）

### 2. **Tactical MCTS（難しいモード）**
- **正式名称**: MCTS with Tactical Heuristics（戦術的ヒューリスティック付きMCTS）
- **特徴**: 勝利手検出・防御ロジック付き
- **強さ**: ★★★★☆（上級者向け）
- **速度**: ★☆☆☆☆（遅いが賢い）

---

## 📊 性能比較

### Pure MCTS（簡単）

```
シミュレーション速度: 123.3回/秒
シミュレーション回数: 617回（5秒）
探索ノード数: 618個
最良手の訪問回数: 2回
最良手の勝率: 50.0%

特徴:
✓ 非常に速い
✓ シンプルな実装
✗ 戦術的に弱い
✗ 王手を見逃す
✗ 防御しない
```

### Tactical MCTS（難しい）

```
シミュレーション速度: 3.1回/秒
シミュレーション回数: 16回（5秒）
探索ノード数: 17個
最良手の訪問回数: 1回
最良手の勝率: 100.0%

特徴:
✓ 戦術的に賢い
✓ 勝利手を見逃さない
✓ 相手の脅威を防御
✓ より正確な評価
✗ 遅い（約40倍）
```

---

## 🔬 技術的な違い

### Pure MCTS のアルゴリズム

```python
def _simulate_pure_random_playout(self, game_state):
    """完全ランダムプレイアウト"""
    while game_state.winner is None:
        legal_moves = game_state.get_legal_moves()
        
        # 完全ランダムに選択
        move = random.choice(legal_moves)
        game_state.apply_move(move)
    
    return game_state.winner
```

**特徴**:
- 単純なランダム選択
- 戦術的な判断なし
- 高速

---

### Tactical MCTS のアルゴリズム

```python
def _simulate_tactical_playout(self, game_state):
    """戦術的ヒューリスティック付きプレイアウト"""
    while game_state.winner is None:
        legal_moves = game_state.get_legal_moves()
        
        # 1. 即座に勝てる手があれば必ず打つ
        winning_move = self._find_winning_move(game_state, legal_moves)
        if winning_move:
            game_state.apply_move(winning_move)
            continue
        
        # 2. 相手の勝利手を防ぐ手があれば優先的に打つ
        blocking_move = self._find_blocking_move(game_state, legal_moves)
        if blocking_move:
            game_state.apply_move(blocking_move)
            continue
        
        # 3. どちらでもなければランダムに選択
        move = random.choice(legal_moves)
        game_state.apply_move(move)
    
    return game_state.winner
```

**特徴**:
- 優先順位付き選択
- 勝利手検出
- 防御ロジック
- より正確だが遅い

---

## 🎮 使い方

### フロントエンド

1. **ゲームモード選択**: 「vsバックエンドAI」を選択
2. **AI難易度選択**: 
   - 「簡単 (Pure MCTS)」: 初心者向け
   - 「難しい (Tactical MCTS)」: 上級者向け

### API

```typescript
// 簡単モード
const response = await apiClient.getAIMove(gameId, -1, 'easy');

// 難しいモード
const response = await apiClient.getAIMove(gameId, -1, 'hard');
```

### Python

```python
from ai.mcts import create_mcts_engine

# Pure MCTS（簡単）
mcts = create_mcts_engine(
    time_limit=10.0,
    use_tactical_heuristics=False
)

# Tactical MCTS（難しい）
mcts = create_mcts_engine(
    time_limit=10.0,
    use_tactical_heuristics=True
)

best_move = mcts.search(game)
```

---

## 📚 学術的な分類

### Pure MCTS
- **カテゴリ**: Classic MCTS
- **アルゴリズム**: 
  - Selection: UCB1
  - Expansion: 未展開ノード
  - Simulation: 完全ランダム
  - Backpropagation: 結果伝播

### Tactical MCTS
- **カテゴリ**: MCTS with Domain Knowledge
- **追加技術**:
  - Tactical Move Ordering（戦術的手順付け）
  - Winning Move Detection（勝利手検出）
  - Threat Detection & Response（脅威検出と対応）
  - Mate Detection（詰み検出）

---

## 🏆 類似する有名なAI

### Pure MCTS
- **類似**: 初期のコンピュータ囲碁AI
- **例**: Crazy Stone（初期版）、Mogo（初期版）

### Tactical MCTS
- **類似**: AlphaGo（ルールベース版）、チェス/将棋AIの静止探索
- **例**: 
  - AlphaGo: MCTS + Neural Networks
  - Stockfish: Minimax + Tactical Heuristics
  - このAI: MCTS + Rule-Based Tactics

---

## 💡 推奨設定

### 9×9盤面
```python
# Pure MCTS
time_limit = 5.0秒
期待シミュレーション: 約600回

# Tactical MCTS
time_limit = 10.0秒
期待シミュレーション: 約30回
```

### 18×18盤面
```python
# Pure MCTS
time_limit = 10.0秒
期待シミュレーション: 約1,200回

# Tactical MCTS
time_limit = 15.0秒
期待シミュレーション: 約45回
```

---

## 🔍 デバッグ情報

### Pure MCTS のログ
```
[MCTS AI] 思考開始（プレイヤー: -1, モード: Pure MCTS）
============================================================
MCTS統計情報
============================================================
シミュレーション回数: 617
探索ノード数: 618
探索時間: 5.00秒
シミュレーション/秒: 123.3
...
```

### Tactical MCTS のログ
```
[MCTS AI] 思考開始（プレイヤー: -1, モード: Tactical MCTS）
============================================================
[MCTS探索開始] 王手を検知！
[状況] 水色がピンクに王手をかけています
[危険度] 相手の勝利手: 3通り
[対策] 防御手を探索します...
============================================================
[王手検知] 水色が王手をかけています！
[ピンチ] ピンクは防御が必要です！
[危険] 相手の勝利手: 3通り
============================================================
[防御成功] 防御手を発見: Move(...)
============================================================
...
```

---

## 🎯 まとめ

### Pure MCTS（簡単）を選ぶべき場合
- ✅ ゲームのルールを学びたい
- ✅ 初心者として練習したい
- ✅ 速いレスポンスが欲しい
- ✅ AIの基本的な動作を理解したい

### Tactical MCTS（難しい）を選ぶべき場合
- ✅ 手応えのある対戦がしたい
- ✅ 戦術的な深さを体験したい
- ✅ AIの賢さを実感したい
- ✅ 上級者として挑戦したい

---

## 📖 参考文献

### MCTS
- Browne, C. et al. (2012). "A Survey of Monte Carlo Tree Search Methods"
- Coulom, R. (2006). "Efficient Selectivity and Backup Operators in Monte-Carlo Tree Search"

### Tactical Heuristics
- Silver, D. et al. (2016). "Mastering the game of Go with deep neural networks and tree search"
- Campbell, M. et al. (2002). "Deep Blue" (チェスAIの戦術的手法)

---

**作成日**: 2024年
**バージョン**: 1.0
**ライセンス**: MIT

