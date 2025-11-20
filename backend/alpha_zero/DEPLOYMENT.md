# Alpha Zeroモデルのデプロイ設定

## 📋 概要

Alpha Zeroモデルは本番環境で自動的にGitHubリリースからダウンロードされます。
このドキュメントでは、デプロイ時の設定方法を説明します。

---

## 🌐 デフォルト設定（推奨）

**何も設定しない場合**、以下のURLから自動的にモデルをダウンロードします：

```
https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar
```

**動作フロー：**
1. アプリ起動時、Alpha Zero AIが初めて使用される
2. ローカルにモデルファイルが見つからない
3. 上記URLから `/tmp/alphazero/best.pth.tar` にダウンロード
4. モデルをメモリにロード
5. 推論実行

**メリット：**
- 環境変数の設定不要
- デプロイが簡単
- 自動的に最新モデルを取得

---

## ⚙️ 環境変数による設定

### 基本設定

| 環境変数名 | 説明 | デフォルト値 | 例 |
|-----------|------|------------|-----|
| `ALPHAZERO_MODEL_PATH` | ローカルモデルファイルのパス | なし | `/var/models/best.pth.tar` |
| `ALPHAZERO_MODEL_URL` | リモートモデルのダウンロードURL | GitHubリリースURL | `https://example.com/model.tar` |
| `ALPHAZERO_MCTS_SIMS` | MCTSシミュレーション回数 | `50` | `100` |

---

## 🚀 デプロイ方法別の設定例

### 1. Vercel（サーバーレス）

#### **設定場所：**
Vercelダッシュボード → Settings → Environment Variables

#### **設定内容：**
```bash
# オプション1: デフォルトURL使用（推奨・設定不要）
# 何も設定しなくても自動ダウンロードされます

# オプション2: カスタムURL使用
ALPHAZERO_MODEL_URL=https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar

# オプション3: MCTSシミュレーション回数を調整（速度優先）
ALPHAZERO_MCTS_SIMS=25
```

#### **注意点：**
- Vercelの `/tmp` ディレクトリは実行ごとに削除される可能性あり
- 初回リクエスト時にダウンロードが走るため、タイムアウトに注意
- 関数タイムアウトを60秒以上に設定することを推奨

---

### 2. Render（Webサービス）

#### **設定場所：**
Renderダッシュボード → Environment → Environment Variables

#### **設定内容：**
```bash
# デフォルトURL使用（推奨）
# 設定不要 - 自動的にダウンロードされます

# またはカスタム設定：
ALPHAZERO_MODEL_URL=https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar
ALPHAZERO_MODEL_PATH=/tmp/alphazero/best.pth.tar
ALPHAZERO_MCTS_SIMS=50
```

#### **メリット：**
- `/tmp` が永続化される場合あり（再ダウンロード不要）
- 十分なタイムアウト設定が可能

---

### 3. AWS（EC2/ECS）

#### **設定方法A: 環境変数（.env）**

```bash
# .env ファイル
ALPHAZERO_MODEL_URL=https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar
ALPHAZERO_MODEL_PATH=/var/app/models/best.pth.tar
ALPHAZERO_MCTS_SIMS=100
```

#### **設定方法B: S3使用（高速化）**

```bash
# S3にモデルをアップロード
aws s3 cp backend/alpha_zero/models/best.pth.tar s3://your-bucket/models/

# 起動スクリプトでダウンロード
#!/bin/bash
aws s3 cp s3://your-bucket/models/best.pth.tar /var/app/models/best.pth.tar

# 環境変数
ALPHAZERO_MODEL_PATH=/var/app/models/best.pth.tar
```

---

### 4. Docker（コンテナ）

#### **方法A: 起動時ダウンロード（推奨）**

```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app

# アプリケーションコードをコピー
COPY . .

# 環境変数はデフォルトのまま（自動ダウンロード）
# または明示的に指定：
ENV ALPHAZERO_MODEL_URL=https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar
ENV ALPHAZERO_MODEL_PATH=/tmp/alphazero/best.pth.tar

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0"]
```

#### **方法B: イメージに埋め込み**

```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app

COPY . .

# モデルをイメージに含める
COPY backend/alpha_zero/models/best.pth.tar /app/models/best.pth.tar

# ローカルパスを指定
ENV ALPHAZERO_MODEL_PATH=/app/models/best.pth.tar

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0"]
```

**方法A vs 方法B:**
- A: イメージサイズ小、デプロイ速、起動遅
- B: イメージサイズ大、デプロイ遅、起動速

---

## 🔧 ローカル開発環境

### 開発時の設定

```bash
# .env.local ファイルを作成
ALPHAZERO_MODEL_PATH=backend/alpha_zero/models/best.pth.tar
ALPHAZERO_MCTS_SIMS=25  # 開発時は少なめで高速化
```

### 動作確認

```bash
# モデルローダーのテスト
cd backend
python -m alpha_zero.model_loader

# Alpha Zero AIプレイヤーのテスト
python -m alpha_zero.AlphaZeroPlayer
```

---

## 📊 優先順位

モデルパスの解決は以下の順序で行われます：

```
1. 引数で明示的に指定されたパス
   ↓ なし
2. 環境変数 ALPHAZERO_MODEL_PATH
   ↓ なし
3. デフォルトのローカルパス
   - alpha_zero/models/best.pth.tar
   - backend/alpha_zero/models/best.pth.tar
   ↓ なし
4. 環境変数 ALPHAZERO_MODEL_URL からダウンロード
   ↓ なし
5. デフォルトURL（GitHubリリース）からダウンロード
   ↓
✅ モデルロード完了
```

---

## 🎯 推奨設定まとめ

### 本番環境（最もシンプル）

```bash
# 環境変数を設定しない
# → 自動的にGitHubリリースからダウンロード
```

### 本番環境（カスタムURL）

```bash
ALPHAZERO_MODEL_URL=https://your-cdn.com/models/best.pth.tar
```

### 開発環境

```bash
ALPHAZERO_MODEL_PATH=backend/alpha_zero/models/best.pth.tar
ALPHAZERO_MCTS_SIMS=25
```

---

## 🚨 トラブルシューティング

### モデルがダウンロードされない

**症状：** `FileNotFoundError: モデルファイルが見つかりません`

**対処法：**
1. ネットワーク接続を確認
2. GitHubリリースURLが正しいか確認
3. 環境変数のスペルミスを確認
4. 手動ダウンロードを試す：
   ```bash
   wget https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar -O /tmp/best.pth.tar
   ```

### ダウンロードが途中で止まる

**症状：** `ダウンロードしたファイルが小さすぎます`

**対処法：**
1. 不完全なファイルを削除：`rm /tmp/alphazero/best.pth.tar`
2. 再起動してリトライ
3. タイムアウト設定を増やす

### メモリ不足

**症状：** `CUDA out of memory` または `MemoryError`

**対処法：**
```bash
# MCTSシミュレーション回数を減らす
ALPHAZERO_MCTS_SIMS=25

# またはGPU使用を無効化（CPU推論）
# backend/alpha_zero/AlphaZeroPlayer.py の 'cuda': True を False に変更
```

---

## 📝 更新履歴

| 日付 | バージョン | 変更内容 |
|-----|----------|---------|
| 2025-11-20 | v1.0 | 初版作成、自動ダウンロード機能実装 |

---

## 🔗 関連リンク

- **GitHubリリース:** https://github.com/Koyo46/wataru-to-dojo/releases/tag/v1.0-alphazero-model
- **モデルファイル直接リンク:** https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar
- **Alpha Zero README:** [backend/alpha_zero/README.md](./README.md)

