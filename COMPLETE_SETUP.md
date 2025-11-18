# 🎉 完全セットアップガイド

バックエンドのデプロイが成功しました！次はフロントエンドとの接続です。

## 📍 現在の状態

✅ **バックエンド**: https://wataru-to-dojo.onrender.com (デプロイ完了！)
⏳ **フロントエンド**: まだローカル環境のみ

## 🔗 接続設定

### 1. バックエンドのCORS設定（Render）

1. https://dashboard.render.com にアクセス
2. `wataru-to-dojo-api` サービスを選択
3. **Environment** タブを開く
4. **Add Environment Variable** をクリック
5. 以下を追加：

```
Key: ALLOWED_ORIGINS
Value: *
```

⚠️ とりあえず全許可（`*`）にしておき、フロントエンドデプロイ後に具体的なURLに変更することを推奨

6. **Save Changes** をクリック

### 2. ローカルでテスト

フロントエンドの環境変数を更新：

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://wataru-to-dojo.onrender.com
```

ローカルで起動してテスト：

```bash
cd frontend
npm run dev
```

http://localhost:3000 にアクセスして、バックエンドAPIと接続できるか確認！

### 3. フロントエンドをデプロイ（Vercel推奨）

#### Vercelでのデプロイ手順：

1. **https://vercel.com** にアクセス
2. GitHubアカウントでログイン
3. **"Add New..."** → **"Project"**
4. GitHubリポジトリを選択
5. 以下の設定：

```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
```

6. **Environment Variables** を追加：

```
NEXT_PUBLIC_API_URL=https://wataru-to-dojo.onrender.com
```

7. **Deploy** をクリック

#### デプロイ完了後：

フロントエンドのURLが決まったら（例: `https://wataru-to-dojo.vercel.app`）、バックエンドのCORS設定を更新：

1. Renderダッシュボードに戻る
2. `ALLOWED_ORIGINS` を更新：

```
ALLOWED_ORIGINS=https://wataru-to-dojo.vercel.app,http://localhost:3000
```

3. **Save Changes** をクリック

## ✅ 動作確認

### バックエンドの確認

```bash
# ヘルスチェック
curl https://wataru-to-dojo.onrender.com/health

# 期待される応答
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "active_games": 0
}
```

### フロントエンドの確認

1. デプロイされたURLにアクセス
2. ブラウザのコンソール（F12）を開く
3. 以下のログが表示されるはずです：

```
✅ API接続成功
🎮 新しいゲームを作成: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

4. ゲームをプレイしてみる！

## 🎮 完成！

これで、ワタルート道場が完全にデプロイされました！

- **フロントエンド**: https://your-app.vercel.app
- **バックエンド**: https://wataru-to-dojo.onrender.com
- **APIドキュメント**: https://wataru-to-dojo.onrender.com/docs

## 📝 環境変数まとめ

### バックエンド（Render）
```
PYTHON_VERSION=3.11.0
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### フロントエンド（Vercel）
```
NEXT_PUBLIC_API_URL=https://wataru-to-dojo.onrender.com
```

### ローカル開発（frontend/.env.local）
```
NEXT_PUBLIC_API_URL=https://wataru-to-dojo.onrender.com
# または
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🐛 トラブルシューティング

### CORSエラーが出る場合

ブラウザコンソールに以下のエラーが表示される：
```
Access to fetch has been blocked by CORS policy
```

**解決方法**:
1. Renderの `ALLOWED_ORIGINS` にフロントエンドのURLが含まれているか確認
2. 含まれていない場合は追加して保存
3. 数秒待ってから再度アクセス

### APIに接続できない場合

画面に以下が表示される：
```
⚠️ APIサーバーに接続できません
```

**解決方法**:
1. バックエンドが起動しているか確認：
   ```bash
   curl https://wataru-to-dojo.onrender.com/health
   ```
2. 無料プランの場合、スリープから復帰するまで30秒〜1分待つ
3. フロントエンドの環境変数が正しいか確認

## 💡 次のステップ

- [ ] カスタムドメインを設定
- [ ] Alpha Zero AIを実装
- [ ] データベースを統合（ゲーム履歴の保存）
- [ ] ユーザー認証を追加
- [ ] オンライン対戦機能を実装

## 🎊 おめでとうございます！

ワタルート道場のデプロイが完了しました！
友達とシェアして遊んでください！

詳細なデプロイガイドは `FRONTEND_DEPLOY.md` を参照してください。

