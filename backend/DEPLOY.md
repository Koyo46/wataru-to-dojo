# Renderへのデプロイガイド

このガイドでは、ワタルート道場のバックエンドをRenderにデプロイする方法を説明します。

## 📋 前提条件

- Renderアカウントを作成済み
- GitHubリポジトリにコードをプッシュ済み

## 🚀 デプロイ手順

### 方法1: render.yamlを使用（推奨）

1. **GitHubリポジトリを接続**
   - Renderダッシュボードにログイン
   - "New" → "Blueprint" を選択
   - GitHubリポジトリを接続
   - `render.yaml` が自動検出される

2. **環境変数を設定（オプション）**
   - `ALLOWED_ORIGINS`: フロントエンドのURL（カンマ区切り）
     ```
     https://your-frontend.vercel.app,https://your-domain.com
     ```

3. **デプロイ**
   - "Apply" をクリック
   - 自動的にビルドとデプロイが開始される

### 方法2: 手動設定

1. **新しいWeb Serviceを作成**
   - Renderダッシュボードで "New" → "Web Service"
   - GitHubリポジトリを選択

2. **設定を入力**
   - **Name**: `wataru-to-dojo-api`
   - **Runtime**: `Python 3`
   - **Root Directory**: `backend` ⚠️ **重要！これを設定しないとモジュールが見つかりません**
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn api.main:app --host 0.0.0.0 --port $PORT
     ```

3. **環境変数を設定**
   - `PYTHON_VERSION`: `3.11.0`
   - `ALLOWED_ORIGINS`: フロントエンドのURL

4. **デプロイ**
   - "Create Web Service" をクリック

## 🔧 トラブルシューティング

### ビルドエラー: Rust関連

**エラー内容**:
```
error: failed to create directory `/usr/local/cargo/registry/cache/...`
Read-only file system (os error 30)
```

**解決方法**:
- `requirements.txt` から `uvicorn[standard]` を `uvicorn` に変更済み
- これでRustの依存関係を回避できます

### モジュールが見つからない

**エラー内容**:
```
ModuleNotFoundError: No module named 'game'
```

**解決方法**:
- `api/main.py` でパスを正しく設定済み
- ビルドコマンドで `backend` ディレクトリに移動していることを確認

### ポートエラー

**エラー内容**:
```
Port 8000 is already in use
```

**解決方法**:
- Renderは自動的に `$PORT` 環境変数を設定します
- `--port $PORT` を使用していることを確認（設定済み）

## 📝 デプロイ後の確認

1. **ヘルスチェック**
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **APIドキュメント**
   - https://your-app.onrender.com/docs
   - https://your-app.onrender.com/redoc

3. **新しいゲームを作成**
   ```bash
   curl -X POST https://your-app.onrender.com/api/game/new \
     -H "Content-Type: application/json" \
     -d '{"board_size": 18}'
   ```

## 🌐 フロントエンドの設定

デプロイ後、フロントエンドの環境変数を更新：

```bash
# frontend/.env.local または Vercel/Netlifyの環境変数
NEXT_PUBLIC_API_URL=https://your-app.onrender.com
```

## 💡 ヒント

### 無料プランの制限

- Renderの無料プランは15分間アクセスがないとスリープします
- 初回アクセス時は起動に30秒〜1分かかる場合があります
- 定期的にアクセスするか、有料プランにアップグレードを検討

### ログの確認

- Renderダッシュボードの "Logs" タブでリアルタイムログを確認
- エラーが発生した場合は、ここで詳細を確認

### カスタムドメイン

- Renderダッシュボードの "Settings" → "Custom Domain" で設定可能
- 無料プランでもカスタムドメインを使用できます

## 🔄 自動デプロイ

GitHubの `main` ブランチにプッシュすると、自動的にデプロイされます：

```bash
git add .
git commit -m "Update backend"
git push origin main
```

## 📊 モニタリング

Renderダッシュボードで以下を確認できます：

- CPU使用率
- メモリ使用率
- リクエスト数
- レスポンス時間

## 🛡️ セキュリティ

本番環境では以下を推奨：

1. **CORS設定を厳格化**
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```

2. **環境変数で機密情報を管理**
   - APIキー
   - データベース接続情報

3. **レート制限を追加**
   ```bash
   pip install slowapi
   ```

## 📚 参考リンク

- [Render公式ドキュメント](https://render.com/docs)
- [FastAPIデプロイガイド](https://fastapi.tiangolo.com/deployment/)
- [トラブルシューティング](https://render.com/docs/troubleshooting-deploys)

