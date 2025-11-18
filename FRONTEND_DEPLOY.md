# フロントエンドのデプロイガイド

## 🚀 Vercelへのデプロイ

### ステップ1: Vercelアカウントの準備

1. https://vercel.com にアクセス
2. GitHubアカウントでサインアップ/ログイン

### ステップ2: プロジェクトのインポート

1. Vercelダッシュボードで **"Add New..."** → **"Project"**
2. GitHubリポジトリを選択
3. **"Import"** をクリック

### ステップ3: プロジェクト設定

#### Framework Preset
```
Framework Preset: Next.js
```

#### Root Directory
```
Root Directory: frontend
```

#### Build and Output Settings
```
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

#### Environment Variables（重要！）

以下の環境変数を追加：

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `https://wataru-to-dojo.onrender.com` |

### ステップ4: デプロイ

1. **"Deploy"** をクリック
2. ビルドが完了するまで待つ（2-3分）
3. デプロイ完了！

### ステップ5: バックエンドのCORS設定を更新

フロントエンドのURLが決まったら、バックエンドの環境変数を更新：

1. Renderダッシュボードで `wataru-to-dojo-api` を選択
2. **Environment** タブを開く
3. `ALLOWED_ORIGINS` を追加/更新：
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
4. **Save Changes** をクリック

## 🎯 動作確認

### 1. フロントエンドにアクセス

```
https://your-app.vercel.app
```

### 2. ブラウザのコンソールを開く（F12）

以下のログが表示されるはずです：

```
✅ API接続成功
🎮 新しいゲームを作成: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 3. ゲームをプレイ

- 対人戦モードまたはvsバックエンドAIモードを選択
- 盤面をクリックして手を配置
- 確定ボタンで手を送信

## 🐛 トラブルシューティング

### CORSエラーが出る

**ブラウザコンソールに表示されるエラー**:
```
Access to fetch at 'https://wataru-to-dojo.onrender.com/api/game/new' 
from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

**解決方法**:

1. Renderダッシュボードで `ALLOWED_ORIGINS` を確認
2. フロントエンドのURLが含まれているか確認
3. 含まれていない場合は追加して保存

### APIに接続できない

**画面に表示されるエラー**:
```
⚠️ APIサーバーに接続できません
```

**解決方法**:

1. バックエンドが起動しているか確認：
   ```bash
   curl https://wataru-to-dojo.onrender.com/health
   ```

2. フロントエンドの環境変数を確認：
   - Vercelダッシュボード → Settings → Environment Variables
   - `NEXT_PUBLIC_API_URL` が正しいか確認

3. 環境変数を変更した場合は再デプロイ：
   - Deployments タブ → 最新のデプロイの右側の "..." → "Redeploy"

### 無料プランのスリープ

Renderの無料プランは15分間アクセスがないとスリープします。

**症状**:
- 初回アクセス時に30秒〜1分待たされる
- "ゲームの作成に失敗しました" エラー

**対策**:
1. もう一度試す（サーバーが起動するまで待つ）
2. UptimeRobotで定期的にpingする
3. 有料プランにアップグレード（$7/月〜）

## 📱 Netlifyへのデプロイ（代替方法）

### ステップ1: Netlifyにログイン

1. https://netlify.com にアクセス
2. GitHubアカウントでログイン

### ステップ2: サイトをインポート

1. **"Add new site"** → **"Import an existing project"**
2. GitHubリポジトリを選択

### ステップ3: ビルド設定

```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/.next
```

### ステップ4: 環境変数

**Site settings** → **Environment variables** で追加：

```
NEXT_PUBLIC_API_URL=https://wataru-to-dojo.onrender.com
```

### ステップ5: デプロイ

**"Deploy site"** をクリック

## 🎨 カスタムドメイン（オプション）

### Vercelの場合

1. プロジェクトを選択
2. **Settings** → **Domains**
3. カスタムドメインを追加

### Netlifyの場合

1. サイトを選択
2. **Domain settings** → **Add custom domain**

## 📊 完成したアーキテクチャ

```
┌─────────────────────┐
│   ユーザー           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Frontend          │
│   (Vercel/Netlify)  │
│                     │
│   Next.js           │
│   TypeScript        │
└──────────┬──────────┘
           │ HTTPS/REST API
           ▼
┌─────────────────────┐
│   Backend           │
│   (Render)          │
│                     │
│   FastAPI           │
│   Python            │
└─────────────────────┘
```

## ✅ デプロイ完了チェックリスト

- [ ] バックエンドがRenderにデプロイされている
- [ ] フロントエンドがVercel/Netlifyにデプロイされている
- [ ] 環境変数 `NEXT_PUBLIC_API_URL` が設定されている
- [ ] バックエンドの `ALLOWED_ORIGINS` が設定されている
- [ ] ブラウザでフロントエンドにアクセスできる
- [ ] API接続成功のログが表示される
- [ ] ゲームがプレイできる

## 🎉 おめでとうございます！

これで、ワタルート道場が完全にデプロイされました！

- **フロントエンド**: https://your-app.vercel.app
- **バックエンド**: https://wataru-to-dojo.onrender.com
- **APIドキュメント**: https://wataru-to-dojo.onrender.com/docs

友達とシェアして遊んでください！🎮

