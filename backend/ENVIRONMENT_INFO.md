# 🎮 ワタルート道場 - 開発環境情報

## 📋 プロジェクト概要
**プロジェクト名:** ワタルート道場（wataru-to_dojo）  
**種類:** 2人対戦ボードゲーム（AI対戦機能付き）  
**アーキテクチャ:** フロントエンド（Next.js）+ バックエンド（FastAPI）

---

## 💻 使用OS

**開発環境:**
- **OS:** Windows 11 (Build 10.0.22631)
- **シェル:** PowerShell
- **文字エンコーディング:** UTF-8（環境変数 `PYTHONIOENCODING='utf-8'` 設定済み）

---

## 🔧 バックエンド（Python）

### 言語バージョン
- **Python:** 3.12（3.10以上推奨）

### Webフレームワーク
- **FastAPI:** 0.115.0（高速なPython Webフレームワーク）
- **Uvicorn:** 0.32.0（ASGIサーバー）
- **Pydantic:** 2.9.0（データバリデーション）

### ライブラリ
- **python-multipart:** 0.0.9（CORS対応）
- **python-dotenv:** 1.0.1（環境変数管理）

### AI実装
- **アルゴリズム:** Monte Carlo Tree Search (MCTS)
  - Pure MCTS（完全ランダムプレイアウト）
  - Tactical MCTS（戦術的ヒューリスティック付き）
- **パフォーマンス:** 約32シミュレーション/秒（9x9盤面）

### 開発ツール
- **仮想環境:** venv
- **パッケージ管理:** pip

---

## 🎨 フロントエンド（JavaScript/TypeScript）

### フレームワーク
- **Next.js:** 16.0.1（React フレームワーク）
- **React:** 19.2.0
- **React DOM:** 19.2.0

### 言語
- **TypeScript:** ^5.x

### CSSフレームワーク
- **Tailwind CSS:** ^4.x
- **@tailwindcss/postcss:** ^4.x

### 開発ツール
- **ESLint:** ^9.x（コード品質チェック）
- **eslint-config-next:** 16.0.1
- **パッケージ管理:** npm

### 型定義
- **@types/node:** ^20.x
- **@types/react:** ^19.x
- **@types/react-dom:** ^19.x

---

## 🛠️ 使用ソフトウェア

### IDE/エディタ
- **Cursor**（AI搭載コードエディタ）
  - Claude Sonnet 4.5 統合

### バージョン管理
- **Git**（ファイル履歴管理）

### サーバー起動
- **開発サーバー（バックエンド）:** `python start_server.py`
  - ポート: 8000
  - URL: http://localhost:8000
  - ドキュメント: http://localhost:8000/docs

- **開発サーバー（フロントエンド）:** `npm run dev`
  - ポート: 3000
  - URL: http://localhost:3000

### 便利スクリプト（PowerShell）
- **カスタムスクリプト:** UTF-8エンコーディング対応で実行
  - 例: `$env:PYTHONIOENCODING='utf-8'; python test_mcts.py`

---

## 📁 プロジェクト構造

```
wataru-to_dojo/
├── backend/                    # バックエンド（Python）
│   ├── game/                   # ゲームロジック
│   │   ├── board.py           # 盤面管理
│   │   ├── move.py            # 手の管理
│   │   └── game.py            # ゲーム状態管理
│   ├── ai/                     # AI実装
│   │   ├── mcts.py            # MCTS実装
│   │   └── __init__.py        # AIエンジン
│   ├── api/                    # APIエンドポイント
│   │   └── main.py            # FastAPI ルート
│   ├── requirements.txt        # Python依存関係
│   ├── start_server.py         # サーバー起動スクリプト
│   ├── test_mcts.py           # MCTSテストスクリプト
│   └── README.md              # バックエンド説明
│
├── frontend/                   # フロントエンド（Next.js）
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx           # メインゲームページ
│   │   ├── layout.tsx         # レイアウト
│   │   └── globals.css        # グローバルスタイル
│   ├── lib/                    # ユーティリティ
│   │   └── api-client.ts      # API通信クライアント
│   ├── package.json           # npm依存関係
│   └── tsconfig.json          # TypeScript設定
│
└── README.md                   # プロジェクト説明
```

---

## 🎯 主要機能

### ゲーム機能
- **盤面サイズ:** 9x9 / 18x18（切り替え可能）
- **ブロックサイズ:** 3マス / 4マス / 5マス
- **プレイモード:** 
  - 2人対戦（人間 vs 人間）
  - AI対戦（人間 vs AI）
- **AI難易度:** 
  - 簡単（Pure MCTS）
  - 難しい（Tactical MCTS）

### パフォーマンス最適化
- **合法手生成キャッシング**（約10倍高速化）
- **MCTSシミュレーション最適化**（約6-7倍高速化）
- **重複手の削除**（探索効率2倍向上）

### セキュリティ
- **CORS設定:** フロントエンドからのAPIアクセス許可
- **入力バリデーション:** Pydanticによる型安全性

---

## 📊 パフォーマンス指標

### MCTS AI（Tactical モード）
- **シミュレーション速度:** 約32回/秒
- **3秒思考:** 約100シミュレーション
- **10秒思考:** 約320シミュレーション
- **勝率:** ランダムAIに対して高い勝率

### 合法手生成
- **キャッシュあり:** 0.0001秒未満（1回目以降）
- **キャッシュなし:** 約0.001秒
- **高速化率:** 約10倍

---

## 🔍 特記事項

### Windows環境対応
- PowerShell での文字化け対策実装済み
- UTF-8エンコーディング設定自動化
- 日本語コンソール出力完全対応

### コード品質
- **型ヒント:** Python全体で型安全性確保
- **TypeScript:** フロントエンド全体で型安全性確保
- **ドキュメント:** 詳細なコメントとREADME完備

---

## 🚀 セットアップ手順

### バックエンド
```powershell
# 1. 仮想環境の作成と有効化
python -m venv venv
venv\Scripts\activate

# 2. 依存関係のインストール
pip install -r requirements.txt

# 3. サーバー起動
python start_server.py
```

### フロントエンド
```powershell
# 1. 依存関係のインストール
cd frontend
npm install

# 2. 開発サーバー起動
npm run dev
```

---

## 📝 テスト実行

### MCTSテスト（クイック）
```powershell
$env:PYTHONIOENCODING='utf-8'
python test_mcts.py --quick --size 9
```

### MCTSテスト（詳細評価）
```powershell
$env:PYTHONIOENCODING='utf-8'
python test_mcts.py --games 10 --size 9
```

---

## 📚 参考ドキュメント

- **バックエンドAPI:** http://localhost:8000/docs（起動後アクセス可能）
- **MCTS詳細:** `backend/ai/README.md`
- **AI難易度比較:** `backend/AI_MODES_README.md`
- **最適化ノート:** `backend/OPTIMIZATION_NOTES.md`

---

## 📅 最終更新日
2025年11月19日

