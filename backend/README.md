# ワタルート道場 - バックエンド

Python + FastAPI で構築されたワタルートゲームのバックエンドAPIサーバーです。

## 構成

- **FastAPI**: 高速なPython Webフレームワーク
- **Python 3.10+**: プログラミング言語
- **Pydantic**: データバリデーション
- **PyTorch**: Alpha Zero学習用（今後実装予定）

## ディレクトリ構造

```
backend/
├── game/              # ゲームルール・状態管理
│   ├── __init__.py    # パッケージ初期化
│   ├── board.py       # 盤面管理 ✅
│   ├── move.py        # 手の管理 ✅
│   └── game.py        # ゲームロジック ✅
├── alpha_zero/        # 学習ロジック（今後実装予定）
│   ├── mcts.py        # モンテカルロ木探索
│   ├── network.py     # ニューラルネットワーク
│   ├── train.py       # 学習スクリプト
│   └── utils.py       # ユーティリティ
├── api/               # APIルート
│   ├── __init__.py    # パッケージ初期化
│   └── main.py        # FastAPIエンドポイント ✅
├── models/            # 学習済みモデル
├── requirements.txt   # Python依存関係
├── test_game.py       # テストスクリプト ✅
└── README.md          # このファイル
```

## セットアップ

### 1. 仮想環境の作成と有効化

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. テストの実行

```bash
cd backend
python test_game.py
```

### 4. APIサーバーの起動

```bash
cd backend
uvicorn api.main:app --reload
```

サーバーが起動したら、以下のURLにアクセスできます：
- API: http://localhost:8000
- ドキュメント: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 実装済みの機能

### ゲームロジック

#### `board.py` - 盤面管理
- 18x18の2層盤面の管理
- セルの状態取得・設定
- 橋の完成判定（勝利条件）
- 隣接セルの取得
- テンソル形式への変換（Alpha Zero用）
- 盤面のクローン・リセット

#### `move.py` - 手の管理
- 手（Move）の表現と検証
- 位置（Position）の管理
- 手の妥当性チェック（MoveValidator）
- 一直線・連続性の検証
- ブロック在庫のチェック

#### `game.py` - ゲームロジック
- ゲーム全体の状態管理
- プレイヤーのブロック在庫管理
- 合法手の生成
- 手の適用と取り消し
- 勝敗判定
- 棋譜のエクスポート・インポート
- ゲーム状態のクローン

### API エンドポイント

#### ゲーム管理
- `POST /api/game/new` - 新しいゲームを作成
- `GET /api/game/{game_id}/state` - ゲーム状態を取得
- `POST /api/game/move` - 手を適用
- `GET /api/game/{game_id}/legal-moves` - 合法手のリストを取得
- `POST /api/game/{game_id}/reset` - ゲームをリセット
- `POST /api/game/{game_id}/undo` - 最後の手を取り消す
- `DELETE /api/game/{game_id}` - ゲームセッションを削除
- `GET /api/games` - 現在のゲームセッション一覧を取得

#### AI機能
- `POST /api/ai/move` - AIの手を取得（ランダム選択）

#### その他
- `GET /` - ルートエンドポイント（API情報）
- `GET /health` - ヘルスチェック
- `GET /api/game/{game_id}/export` - 棋譜をエクスポート

## API使用例

### 新しいゲームを作成

```bash
curl -X POST "http://localhost:8000/api/game/new" \
  -H "Content-Type: application/json" \
  -d '{"board_size": 18}'
```

### 手を適用

```bash
curl -X POST "http://localhost:8000/api/game/move" \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "your-game-id",
    "move": {
      "player": 1,
      "path": [
        {"row": 0, "col": 0, "layer": 0},
        {"row": 0, "col": 1, "layer": 0},
        {"row": 0, "col": 2, "layer": 0}
      ]
    }
  }'
```

### 合法手を取得

```bash
curl -X GET "http://localhost:8000/api/game/{game_id}/legal-moves"
```

### AIの手を取得

```bash
curl -X POST "http://localhost:8000/api/ai/move" \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "your-game-id",
    "player": 1
  }'
```

## ゲームルール

### 基本ルール
- 18x18の盤面で2人のプレイヤー（水色・ピンク）が対戦
- 各プレイヤーは3マス（無限）、4マス（1個）、5マス（1個）のブロックを持つ
- ブロックは一直線に配置する
- 盤面は2層構造（レイヤー1とレイヤー2）

### 配置ルール
- **レイヤー1モード**: 空いているマスに配置
- **レイヤー2モード（橋渡し）**: 自分の色のマスの上に配置可能

### 勝利条件
- **水色**: 上端から下端まで自分の色で繋ぐ
- **ピンク**: 左端から右端まで自分の色で繋ぐ

## 今後の実装予定

1. ✅ ゲームロジックの実装（board.py, move.py, game.py）
2. ✅ FastAPI エンドポイントの実装
3. ⏳ Alpha Zero 学習ロジックの実装
   - モンテカルロ木探索（MCTS）
   - ニューラルネットワーク
   - 自己対戦による学習
4. ⏳ モデルの学習とデプロイ
5. ⏳ データベース統合（ゲーム履歴の永続化）
6. ⏳ ユーザー認証機能

## 開発者向け情報

### コード構造

- `Board`: 盤面の状態を管理
- `Move` / `Position`: 手と位置の表現
- `MoveValidator`: 手の妥当性を検証
- `PlayerBlocks`: プレイヤーのブロック在庫を管理
- `WataruToGame`: ゲーム全体のロジックを統括

### テスト

```bash
# 基本的なゲームフローのテスト
python test_game.py
```

### デバッグ

FastAPIの自動生成ドキュメントを使用してAPIをテストできます：
- http://localhost:8000/docs （Swagger UI）
- http://localhost:8000/redoc （ReDoc）

## ライセンス

このプロジェクトは個人開発用です。

