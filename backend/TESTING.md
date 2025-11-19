# ワタルート道場 - テストガイド

このドキュメントでは、ワタルート道場のバックエンドをテストする方法をまとめています。

## 📋 目次

1. [クイックスタート](#クイックスタート)
2. [基本的なゲームロジックのテスト](#基本的なゲームロジックのテスト)
3. [AI（MCTS）のテスト](#aimctsのテスト)
4. [パフォーマンステスト](#パフォーマンステスト)
5. [APIサーバーのテスト](#apiサーバーのテスト)
6. [トラブルシューティング](#トラブルシューティング)

---

## クイックスタート

### 前提条件

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### すべてのテストを実行

```bash
# 基本テスト
python test_game.py

# AI性能テスト（短時間）
python test_mcts.py --quick

# パフォーマンステスト
python test_performance.py
```

---

## 基本的なゲームロジックのテスト

### test_game.py

**目的**: ゲームの基本機能が正しく動作するか確認

**実行方法**:
```bash
python test_game.py
```

**テスト内容**:
- ✅ ゲームの初期化
- ✅ 合法手の生成
- ✅ 手の適用
- ✅ 勝敗判定
- ✅ レイヤー2（橋渡し）機能

**期待される出力**:
```
=== ワタルートゲーム テスト ===

✓ ゲーム作成: 18x18
✓ 合法手の数: 1020
✓ 手の適用成功
✓ 勝者判定: ピンク
=== テスト完了 ===
```

---

## AI（MCTS）のテスト

### test_mcts.py

**目的**: MCTS AIの性能と動作を評価

#### オプション一覧

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--quick` | 1ゲームのクイックテスト | - |
| `--games N` | N回のゲームを実行 | 10 |
| `--time T` | AI思考時間（秒） | 5.0 |
| `--size N` | 盤面サイズ | 9 |
| `--show-board` | 一手ごとに盤面を表示 | False |

#### 実行例

**1. クイックテスト（1ゲーム）**
```bash
python test_mcts.py --quick
```
最速でAIの動作確認ができます。

**2. 標準評価（10ゲーム）**
```bash
python test_mcts.py --games 10 --time 5.0
```
MCTS vs ランダムAIで10回対戦し、勝率を測定します。

**3. 高精度評価（100ゲーム、長時間思考）**
```bash
python test_mcts.py --games 100 --time 10.0
```
本格的な性能評価。時間がかかります（30分〜1時間）。

**4. 小さい盤面でテスト**
```bash
python test_mcts.py --size 9 --games 20
```
9×9の小さい盤面で高速テスト。

**5. 盤面を視覚化しながらテスト**
```bash
python test_mcts.py --quick --show-board
```
一手ごとに盤面を表示します。ゲームの流れを確認できます。

#### 期待される出力

**クイックテスト**:
```
============================================================
MCTS vs ランダムAI - クイックテスト
============================================================
盤面サイズ: 9x9
思考時間: 5.0秒/手
============================================================

[テスト 1/1] MCTS(水色) vs ランダム(ピンク)
  ターン 1: MCTS思考中... 完了
  ターン 2: ランダム選択
  ...
  ターン 15: MCTS思考中... 完了
  
結果: 水色 の勝利！

============================================================
テスト完了
============================================================
```

**標準評価**:
```
============================================================
MCTS vs ランダムAI - 評価テスト
============================================================
対戦回数: 10
盤面サイズ: 9x9
思考時間: 5.0秒/手
============================================================

[MCTS先手] ゲーム 1/5 → 水色勝利 (25手)
[MCTS先手] ゲーム 2/5 → 水色勝利 (18手)
...
[MCTS後手] ゲーム 6/10 → ピンク勝利 (22手)
...

============================================================
最終結果
============================================================
総対戦数: 10
MCTS勝利: 9回 (90.0%)
ランダム勝利: 1回 (10.0%)

MCTS先手（水色）: 5/5 (100.0%)
MCTS後手（ピンク）: 4/5 (80.0%)

平均手数: 21.3手
============================================================
```

---

## パフォーマンステスト

### test_performance.py

**目的**: `get_legal_moves()` の速度を測定

**実行方法**:
```bash
python test_performance.py
```

**テスト内容**:
- 初期状態での合法手生成速度
- キャッシュの効果
- 盤面サイズ別の性能比較

**期待される出力**:
```
============================================================
パフォーマンステスト: 9x9盤面
============================================================
合法手の数: 420

キャッシュなし（100回）: 0.0234秒 (0.234ms/回)
キャッシュあり（100回）: 0.0001秒 (0.001ms/回)
高速化: 234.0倍

初回生成時間: 0.0003秒
============================================================
```

**ベンチマーク目安**:
- 9×9盤面: 0.1〜0.5ms/回
- 18×18盤面: 0.5〜2.0ms/回

これより遅い場合は、ゲームロジックに問題がある可能性があります。

---

## APIサーバーのテスト

### サーバー起動

```bash
python start_server.py
```

### 1. ヘルスチェック

**ブラウザで**:
```
http://localhost:8000/health
```

**期待されるレスポンス**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000000",
  "active_games": 0
}
```

### 2. API ドキュメント

ブラウザで以下にアクセス：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. 手動APIテスト

**新しいゲームを作成**:
```bash
curl -X POST "http://localhost:8000/api/game/new?board_size=18" \
     -H "Content-Type: application/json"
```

**AIの手を取得**:
```bash
curl -X POST "http://localhost:8000/api/ai/move" \
     -H "Content-Type: application/json" \
     -d '{"game_id": "YOUR_GAME_ID", "player": -1}'
```

### 4. フロントエンドとの統合テスト

```bash
# ターミナル1: バックエンド起動
cd backend
python start_server.py

# ターミナル2: フロントエンド起動
cd frontend
npm run dev

# ブラウザで http://localhost:3000 にアクセス
```

---

## プレイアウト視覚化テスト

### test_playout_visualization.py

**目的**: MCTSのシミュレーション過程を可視化

**実行方法**:
```bash
python test_playout_visualization.py
```

**用途**:
- MCTSの内部動作を理解する
- デバッグ用
- プレイアウトでどのような手を選んでいるか確認

**注意**: 非常に詳細な出力が表示されるため、通常の性能テストには使用しないでください。

---

## テストシナリオ別ガイド

### 🎯 シナリオ1: 新機能を追加した後

```bash
# 1. 基本ロジックが壊れていないか確認
python test_game.py

# 2. AIが正常に動作するか確認
python test_mcts.py --quick

# 3. パフォーマンスが劣化していないか確認
python test_performance.py
```

### 🐛 シナリオ2: バグ修正後

```bash
# 1. 該当機能の基本テスト
python test_game.py

# 2. AI対戦で異常な動作がないか確認（盤面表示付き）
python test_mcts.py --quick --show-board
```

### 🚀 シナリオ3: パフォーマンス最適化後

```bash
# 1. パフォーマンステスト（最適化前後で比較）
python test_performance.py

# 2. AI性能に影響がないか確認
python test_mcts.py --games 20
```

### 📊 シナリオ4: AI強化後

```bash
# 1. 小盤面で短時間テスト
python test_mcts.py --size 9 --games 20 --time 3.0

# 2. 標準盤面で詳細評価
python test_mcts.py --size 18 --games 50 --time 5.0

# 3. 長時間思考での性能
python test_mcts.py --size 18 --games 20 --time 15.0
```

---

## トラブルシューティング

### ❌ ModuleNotFoundError

**問題**: `ModuleNotFoundError: No module named 'game'`

**解決策**:
```bash
cd backend  # backendディレクトリにいることを確認
python test_game.py
```

### ❌ パフォーマンスが遅い

**問題**: `get_legal_moves()` が10ms以上かかる

**チェック項目**:
1. キャッシュが有効か確認
2. レイヤー2の手生成ロジックに無限ループがないか
3. 重複した手が生成されていないか

**診断**:
```bash
python test_performance.py  # 詳細な性能情報を確認
```

### ❌ AI が頓珍漢な手を打つ

**問題**: MCTSが明らかに悪い手を選ぶ

**チェック項目**:
1. 思考時間が十分か（最低5秒推奨）
2. シミュレーション回数が少なすぎないか
3. 詰みの状態でないか

**診断**:
```bash
python test_mcts.py --quick --show-board  # 盤面を表示して確認
```

### ❌ API接続エラー

**問題**: フロントエンドから「APIサーバーに接続できません」

**チェック項目**:
1. バックエンドが起動しているか
   ```bash
   curl http://localhost:8000/health
   ```
2. CORSエラーがないかブラウザのコンソールで確認
3. ファイアウォールでポート8000がブロックされていないか

---

## テスト結果の目安

### ✅ 合格基準

| テスト | 合格基準 |
|--------|---------|
| **基本ロジック** | すべてのテストがパス |
| **MCTS vs ランダム（9×9）** | 勝率 80% 以上 |
| **MCTS vs ランダム（18×18）** | 勝率 70% 以上 |
| **パフォーマンス（9×9）** | < 0.5ms/回 |
| **パフォーマンス（18×18）** | < 2.0ms/回 |
| **APIヘルスチェック** | 200 OK |

### ⚠️ 注意が必要

- MCTS勝率が50%未満 → AIロジックに問題
- パフォーマンスが目安の3倍以上 → 最適化が必要
- APIが500エラー → サーバーログを確認

---

## CI/CD での実行

### GitHub Actions 例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run basic tests
        run: |
          cd backend
          python test_game.py
      - name: Run performance tests
        run: |
          cd backend
          python test_performance.py
      - name: Run AI tests
        run: |
          cd backend
          python test_mcts.py --quick
```

---

## まとめ

### 日常的なテスト（開発中）
```bash
python test_game.py && python test_mcts.py --quick
```

### リリース前のフルテスト
```bash
python test_game.py
python test_performance.py
python test_mcts.py --games 50 --time 5.0
```

### 詳細デバッグ
```bash
python test_mcts.py --quick --show-board
python test_playout_visualization.py
```

---

## 参考リンク

- [AI実装ドキュメント](AI_MODES_README.md)
- [環境情報](ENVIRONMENT_INFO.md)
- [最適化ノート](OPTIMIZATION_NOTES.md)
- [バックエンドREADME](README.md)

