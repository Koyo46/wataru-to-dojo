# ワタルート道場 - セットアップガイド

バックエンドとフロントエンドを連携させて、ゲームをプレイする方法を説明します。

## 📋 前提条件

- **Python 3.10+** がインストールされていること
- **Node.js 18+** がインストールされていること
- **npm** または **yarn** がインストールされていること

## 🚀 クイックスタート

### ステップ1: バックエンドのセットアップ

#### 1-1. 仮想環境の作成と有効化

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

#### 1-2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

#### 1-3. テストの実行（オプション）

```bash
python test_game.py
```

#### 1-4. APIサーバーの起動

```bash
python start_server.py
```

または

```bash
uvicorn api.main:app --reload
```

✅ バックエンドが http://localhost:8000 で起動します。

### ステップ2: フロントエンドのセットアップ

**新しいターミナルを開いて**、以下を実行：

#### 2-1. 依存関係のインストール

```bash
cd frontend
npm install
```

#### 2-2. 環境変数の設定（オプション）

デフォルトでは `http://localhost:8000` に接続します。
変更する場合は `.env.local` ファイルを作成：

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 2-3. 開発サーバーの起動

```bash
npm run dev
```

✅ フロントエンドが http://localhost:3000 で起動します。

### ステップ3: ゲームをプレイ

1. ブラウザで http://localhost:3000 を開く
2. ゲームモードを選択：
   - **対人戦**: 2人で交互にプレイ
   - **vsバックエンドAI**: AIと対戦
3. 盤面をクリックして手を配置
4. 3マス以上配置したら「確定」ボタンをクリック

## 🎮 ゲームの遊び方

### 基本ルール

- **水色プレイヤー**: 上端から下端まで自分の色で繋ぐ
- **ピンクプレイヤー**: 左端から右端まで自分の色で繋ぐ
- 先に橋を完成させたプレイヤーの勝ち

### ブロックの種類

- **3マスブロック**: 無限に使用可能
- **4マスブロック**: 1個のみ
- **5マスブロック**: 1個のみ

### 配置ルール

1. **一直線**: ブロックは横または縦に一直線に配置
2. **連続**: 隣接するマスに配置
3. **2層構造**: 
   - レイヤー1: 空いているマスに配置
   - レイヤー2: 自分の色のマスの上に配置（橋渡し）

### 操作方法

1. **起点を選択**: 空いているマス、または自分の色のマスをクリック
2. **ブロックを配置**: 隣接するマスを順番にクリック
3. **確定**: 3マス以上配置したら「確定」ボタンをクリック
4. **キャンセル**: 配置をやり直す場合は「キャンセル」ボタンをクリック

## 🔧 トラブルシューティング

### APIサーバーに接続できない

**症状**: 画面に「⚠️ APIサーバーに接続できません」と表示される

**解決方法**:
1. バックエンドAPIサーバーが起動しているか確認
   ```bash
   # バックエンドのターミナルで
   python start_server.py
   ```
2. http://localhost:8000/health にアクセスして確認
3. ファイアウォールやセキュリティソフトがポート8000をブロックしていないか確認

### CORSエラー

**症状**: ブラウザのコンソールに「CORS policy」エラーが表示される

**解決方法**:
1. バックエンドの `api/main.py` でCORS設定を確認
2. フロントエンドのURLが許可リストに含まれているか確認
3. バックエンドを再起動

### ゲームが動作しない

**解決方法**:
1. ブラウザのコンソール（F12）でエラーを確認
2. バックエンドのログを確認
3. ページをリロード（Ctrl+R または Cmd+R）
4. ブラウザのキャッシュをクリア

### ポートが既に使用されている

**症状**: 
- `Address already in use` エラー
- `Port 8000 is already in use` エラー

**解決方法**:

**Windows:**
```bash
# ポート8000を使用しているプロセスを確認
netstat -ano | findstr :8000

# プロセスIDを確認してタスクマネージャーで終了
```

**Linux/Mac:**
```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>
```

## 📚 APIドキュメント

バックエンドが起動したら、以下のURLでAPIドキュメントを確認できます：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ 開発者向け情報

### ディレクトリ構造

```
wataru-to_dojo/
├── backend/              # バックエンド（Python + FastAPI）
│   ├── api/              # APIエンドポイント
│   ├── game/             # ゲームロジック
│   ├── test_game.py      # テストスクリプト
│   └── start_server.py   # サーバー起動スクリプト
├── frontend/             # フロントエンド（Next.js + TypeScript）
│   ├── app/              # Next.js App Router
│   ├── lib/              # ユーティリティ（APIクライアント）
│   ├── types/            # 型定義
│   └── components/       # Reactコンポーネント
└── SETUP.md              # このファイル
```

### 技術スタック

**バックエンド:**
- Python 3.10+
- FastAPI
- Pydantic
- Uvicorn

**フロントエンド:**
- Next.js 15
- TypeScript
- Tailwind CSS
- React 19

### 開発モード

**バックエンド（ホットリロード）:**
```bash
cd backend
uvicorn api.main:app --reload
```

**フロントエンド（ホットリロード）:**
```bash
cd frontend
npm run dev
```

### 本番ビルド

**フロントエンド:**
```bash
cd frontend
npm run build
npm start
```

## 🎯 次のステップ

- [ ] Alpha Zero AIの実装
- [ ] データベース統合
- [ ] ユーザー認証
- [ ] オンライン対戦機能
- [ ] 棋譜の保存・再生

## 📝 ライセンス

このプロジェクトは個人開発用です。

## 🤝 サポート

問題が発生した場合は、以下を確認してください：

1. Python、Node.jsのバージョン
2. 依存関係が正しくインストールされているか
3. ポートが空いているか
4. ファイアウォール設定

それでも解決しない場合は、GitHubのIssueを作成してください。

