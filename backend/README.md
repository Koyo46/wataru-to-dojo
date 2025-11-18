# ワタルート道場 - バックエンド

Python + FastAPI で構築されたワタルートゲームのバックエンドAPIサーバーです。

## 構成

- **FastAPI**: 高速なPython Webフレームワーク
- **Python 3.10+**: プログラミング言語
- **PyTorch**: Alpha Zero学習用（予定）

## ディレクトリ構造

```
backend/
├── game/              # ゲームルール・状態管理
│   ├── board.py       # 盤面管理
│   ├── move.py        # 手の管理
│   └── game.py        # ゲームロジック
├── alpha_zero/        # 学習ロジック
│   ├── mcts.py        # モンテカルロ木探索
│   ├── network.py     # ニューラルネットワーク
│   ├── train.py       # 学習スクリプト
│   └── utils.py       # ユーティリティ
├── api/               # APIルート
│   └── main.py        # FastAPIエンドポイント
├── models/            # 学習済みモデル
├── requirements.txt   # Python依存関係
└── README.md          # このファイル
```

## セットアップ（予定）

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Windows）
venv\Scripts\activate

# 仮想環境の有効化（Linux/Mac）
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# APIサーバーの起動
uvicorn api.main:app --reload
```

## API エンドポイント（予定）

- `GET /api/game/new` - 新しいゲームを開始
- `POST /api/game/move` - 手を送信
- `GET /api/game/state` - 現在のゲーム状態を取得
- `POST /api/ai/move` - AIの手を取得

## 今後の実装予定

1. ゲームロジックの実装（board.py, move.py, game.py）
2. FastAPI エンドポイントの実装
3. Alpha Zero 学習ロジックの実装
4. モデルの学習とデプロイ

