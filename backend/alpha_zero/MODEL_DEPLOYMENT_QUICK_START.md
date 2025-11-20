# Alpha Zeroモデル デプロイ クイックスタート

## 🚀 最も簡単な方法（推奨）

### 本番環境

**何もしない** → 自動的にGitHubリリースからダウンロードされます！

```bash
# 環境変数不要
# デプロイするだけでOK
```

アプリ起動時、初めてAlpha Zero AIが使われるときに自動的に以下を実行：
1. ローカルにモデルがあるか確認
2. なければ自動ダウンロード: `https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar`
3. `/tmp/alphazero/best.pth.tar` に保存
4. モデルをロード

---

## ⚙️ カスタマイズが必要な場合

### 環境変数

```bash
# 方法1: カスタムURLを使う
ALPHAZERO_MODEL_URL=https://your-custom-url.com/model.tar

# 方法2: ローカルパスを指定（事前ダウンロード済み）
ALPHAZERO_MODEL_PATH=/var/models/best.pth.tar

# 方法3: MCTSシミュレーション回数を調整（速度調整）
ALPHAZERO_MCTS_SIMS=25  # デフォルト: 50
```

---

## 🧪 動作確認

```bash
# 1. モデルローダーのテスト
cd backend
python -m alpha_zero.model_loader

# 2. Alpha Zero AIプレイヤーのテスト
python -m alpha_zero.AlphaZeroPlayer
```

---

## 📋 デプロイ先別の設定

### Vercel
```
環境変数不要（デフォルトで動作）

または:
ALPHAZERO_MCTS_SIMS=25  # 速度優先の場合
```

### Render
```
環境変数不要（デフォルトで動作）
```

### AWS/GCP/Azure
```
環境変数不要（デフォルトで動作）

またはS3等を使う場合:
ALPHAZERO_MODEL_URL=https://your-storage.com/model.tar
```

### Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .

# 環境変数不要（デフォルトで動作）
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0"]
```

---

## 🔧 トラブルシューティング

### Q: ダウンロードに失敗する
```bash
# 手動ダウンロードして確認
wget https://github.com/Koyo46/wataru-to-dojo/releases/download/v1.0-alphazero-model/best.pth.tar

# 環境変数で手動ダウンロード先を指定
ALPHAZERO_MODEL_PATH=/path/to/downloaded/best.pth.tar
```

### Q: 起動が遅い
```bash
# MCTSシミュレーション回数を減らす
ALPHAZERO_MCTS_SIMS=25
```

### Q: メモリ不足
```bash
# シミュレーション回数を減らす
ALPHAZERO_MCTS_SIMS=10
```

---

## 📚 詳細ドキュメント

詳しい設定は [DEPLOYMENT.md](./DEPLOYMENT.md) を参照してください。

---

## ✅ まとめ

- **開発環境**: ローカルのモデルファイルを自動検出
- **本番環境**: 環境変数不要、自動ダウンロード
- **カスタマイズ**: 環境変数で柔軟に設定可能

**→ 基本的には何もしなくてOK！** 🎉

