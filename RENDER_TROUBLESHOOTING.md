# Renderデプロイ - トラブルシューティング

## 🐛 よくあるエラーと解決方法

### エラー1: ModuleNotFoundError: No module named 'app'

**エラーメッセージ**:
```
ModuleNotFoundError: No module named 'app'
```

**原因**: 
- Root Directoryが設定されていない
- 起動コマンドが間違っている

**解決方法**:

#### render.yamlを使用している場合:
```yaml
services:
  - type: web
    name: wataru-to-dojo-api
    runtime: python
    plan: free
    rootDir: backend  # ← これが重要！
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

#### 手動設定の場合:
1. Renderダッシュボードで該当サービスを選択
2. "Settings" タブを開く
3. "Root Directory" を `backend` に設定
4. "Build Command" を `pip install -r requirements.txt` に設定
5. "Start Command" を `uvicorn api.main:app --host 0.0.0.0 --port $PORT` に設定
6. "Save Changes" をクリック

---

### エラー2: Rustビルドエラー

**エラーメッセージ**:
```
error: failed to create directory `/usr/local/cargo/registry/cache/...`
Read-only file system (os error 30)
💥 maturin failed
```

**原因**: 
- `uvicorn[standard]` がRustの依存関係を含んでいる

**解決方法**:

`backend/requirements.txt` を確認：
```txt
# ❌ 間違い
uvicorn[standard]==0.24.0

# ✅ 正しい
uvicorn==0.32.0
```

---

### エラー3: Pythonバージョンエラー

**エラーメッセージ**:
```
Python version 3.13 is not supported
```

**解決方法**:

1. `backend/runtime.txt` を作成：
   ```txt
   python-3.11.0
   ```

2. または環境変数で設定：
   - Renderダッシュボード → Settings → Environment
   - `PYTHON_VERSION` = `3.11.0`

---

### エラー4: ポートエラー

**エラーメッセージ**:
```
Port 8000 is already in use
```

**原因**: 
- 起動コマンドで `$PORT` を使用していない

**解決方法**:

起動コマンドを確認：
```bash
# ❌ 間違い
uvicorn api.main:app --host 0.0.0.0 --port 8000

# ✅ 正しい
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

---

### エラー5: requirements.txtが見つからない

**エラーメッセージ**:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'backend/requirements.txt'
```

**原因**: 
- Root Directoryが設定されているのに、ビルドコマンドで `backend/` を指定している

**解決方法**:

Root Directoryを `backend` に設定した場合：
```bash
# ❌ 間違い
pip install -r backend/requirements.txt

# ✅ 正しい
pip install -r requirements.txt
```

---

### エラー6: CORSエラー

**エラーメッセージ** (ブラウザコンソール):
```
Access to fetch at 'https://your-api.onrender.com/api/game/new' 
from origin 'https://your-frontend.vercel.app' has been blocked by CORS policy
```

**解決方法**:

1. Renderダッシュボード → Settings → Environment
2. 環境変数を追加：
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com
   ```
3. サービスを再デプロイ

---

## 🔍 デバッグ方法

### 1. ログを確認

Renderダッシュボード → Logs タブ

重要なログメッセージ：
- `✅ Application startup complete` - 起動成功
- `❌ ModuleNotFoundError` - モジュールが見つからない
- `❌ ImportError` - インポートエラー

### 2. ヘルスチェック

デプロイ後、以下のコマンドでAPIが動作しているか確認：

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

### 3. APIドキュメントを確認

ブラウザで以下にアクセス：
- https://your-app.onrender.com/docs
- https://your-app.onrender.com/redoc

これらが表示されれば、APIは正常に動作しています。

---

## 📋 チェックリスト

デプロイ前に以下を確認：

- [ ] `backend/requirements.txt` に `uvicorn[standard]` が含まれていない
- [ ] `render.yaml` に `rootDir: backend` が設定されている
- [ ] 起動コマンドが `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- [ ] `backend/runtime.txt` に `python-3.11.0` が記載されている
- [ ] GitHubにすべての変更がプッシュされている

---

## 🛠️ 手動デプロイ設定の完全ガイド

Renderダッシュボードでの設定（スクリーンショット代わり）：

### Basic Settings
```
Name: wataru-to-dojo-api
Runtime: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: backend  ⚠️ 重要！
```

### Build & Deploy
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables
```
PYTHON_VERSION = 3.11.0
ALLOWED_ORIGINS = https://your-frontend.vercel.app
```

### Plan
```
Instance Type: Free
```

---

## 🚀 デプロイ後の確認手順

1. **ビルドログを確認**
   ```
   ==> Installing dependencies
   ==> Build successful
   ```

2. **起動ログを確認**
   ```
   ==> Starting service
   INFO:     Started server process
   INFO:     Application startup complete
   ```

3. **ヘルスチェック**
   ```bash
   curl https://your-app.onrender.com/health
   ```

4. **APIドキュメント確認**
   - https://your-app.onrender.com/docs

5. **フロントエンドから接続テスト**
   - フロントエンドの環境変数を更新
   - ゲームを開始してAPIと通信できるか確認

---

## 💡 よくある質問

### Q: デプロイに時間がかかる

**A**: 初回デプロイは5-10分かかることがあります。無料プランの場合、ビルドリソースが制限されているためです。

### Q: サービスがスリープする

**A**: 無料プランでは15分間アクセスがないとスリープします。以下の対策があります：
- UptimeRobotなどで定期的にpingする
- 有料プランにアップグレード（$7/月〜）

### Q: ゲームセッションが消える

**A**: 現在、セッションはメモリに保存されています。サーバー再起動で消えます。本番環境ではRedisなどの永続化ストレージを推奨します。

---

## 📞 サポート

それでも解決しない場合：

1. Renderの公式ドキュメントを確認
   - https://render.com/docs/troubleshooting-deploys

2. GitHubのIssueを作成
   - ログの全文を添付
   - 設定のスクリーンショットを添付

3. Renderのサポートに連絡
   - https://render.com/support

