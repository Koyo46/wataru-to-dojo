# Renderデプロイエラーの修正

## 🐛 発生したエラー

```
error: failed to create directory `/usr/local/cargo/registry/cache/...`
Read-only file system (os error 30)
💥 maturin failed
```

このエラーは、Rustのビルドツール（maturin）が必要なパッケージをインストールしようとして失敗していました。

## 🔧 修正内容

### 1. `requirements.txt` の更新

**問題**: `uvicorn[standard]` がRustベースの依存関係を含んでいた

**修正前**:
```txt
uvicorn[standard]==0.24.0
```

**修正後**:
```txt
uvicorn==0.32.0
```

`[standard]` オプションを削除することで、Rustの依存関係を回避しました。

### 2. パッケージバージョンの更新

より新しく安定したバージョンに更新：

```txt
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.9.0
python-multipart==0.0.9
python-dotenv==1.0.1
```

### 3. Render設定ファイルの追加

#### `render.yaml` (プロジェクトルート)
```yaml
services:
  - type: web
    name: wataru-to-dojo-api
    runtime: python
    plan: free
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

**重要**: `rootDir: backend` を指定することで、Renderは `backend` ディレクトリをルートとして認識します。

#### `backend/runtime.txt`
```txt
python-3.11.0
```

#### `backend/Procfile`
```txt
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### 4. CORS設定の改善

環境変数でオリジンを管理できるように修正：

```python
import os

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 デプロイ手順

### 方法1: render.yaml を使用（推奨）

1. GitHubにコードをプッシュ
   ```bash
   git add .
   git commit -m "Fix Render deployment"
   git push origin main
   ```

2. Renderダッシュボードで "New" → "Blueprint" を選択

3. GitHubリポジトリを接続

4. `render.yaml` が自動検出され、デプロイが開始される

### 方法2: 手動設定

1. Renderダッシュボードで "New" → "Web Service"

2. 以下の設定を入力：
   - **Name**: `wataru-to-dojo-api`
   - **Runtime**: `Python 3`
   - **Root Directory**: `backend` ⚠️ **重要！**
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn api.main:app --host 0.0.0.0 --port $PORT
     ```

3. 環境変数を設定（オプション）：
   - `PYTHON_VERSION`: `3.11.0`
   - `ALLOWED_ORIGINS`: フロントエンドのURL

## ✅ デプロイ前のチェック

デプロイ前に以下のスクリプトを実行して確認：

```bash
cd backend
python check_deploy.py
```

すべてのチェックが成功すれば、デプロイの準備完了です。

## 🔍 デプロイ後の確認

### 1. ヘルスチェック

```bash
curl https://your-app.onrender.com/health
```

期待される応答：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "active_games": 0
}
```

### 2. APIドキュメント

ブラウザで以下にアクセス：
- https://your-app.onrender.com/docs
- https://your-app.onrender.com/redoc

### 3. 新しいゲームを作成

```bash
curl -X POST https://your-app.onrender.com/api/game/new \
  -H "Content-Type: application/json" \
  -d '{"board_size": 18}'
```

## 📝 フロントエンドの設定

デプロイ後、フロントエンドの環境変数を更新：

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://your-app.onrender.com
```

Vercel/Netlifyでデプロイする場合は、環境変数設定画面で追加してください。

## 💡 重要な注意点

### 無料プランの制限

- **スリープ**: 15分間アクセスがないとスリープ状態になります
- **起動時間**: スリープから復帰には30秒〜1分かかります
- **対策**: 
  - 定期的にアクセスする
  - UptimeRobotなどのモニタリングサービスを使用
  - 有料プランにアップグレード

### セッション管理

現在、ゲームセッションはメモリに保存されています：
- サーバー再起動でセッションが失われます
- 本番環境ではRedisなどの永続化ストレージを推奨

## 🎉 修正完了

これで、Renderへのデプロイが成功するはずです！

問題が解決しない場合は、以下を確認してください：
1. `requirements.txt` に `uvicorn[standard]` が含まれていないこと
2. Python 3.11.0 を使用していること
3. ビルドログでエラーの詳細を確認

## 📚 参考資料

- [backend/DEPLOY.md](backend/DEPLOY.md) - 詳細なデプロイガイド
- [Render公式ドキュメント](https://render.com/docs)
- [FastAPIデプロイガイド](https://fastapi.tiangolo.com/deployment/)

