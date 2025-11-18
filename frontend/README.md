# ワタルート道場 - フロントエンド

Next.js + TypeScript + Tailwind CSS で構築されたワタルートゲームのフロントエンドアプリケーションです。

## 構成

- **Next.js 15**: Reactフレームワーク
- **TypeScript**: 型安全な開発
- **Tailwind CSS**: ユーティリティファーストCSSフレームワーク

## セットアップ

### 1. 依存関係のインストール

```bash
npm install
```

### 2. 環境変数の設定

`.env.local`ファイルを作成（または`.env.local.example`をコピー）：

```bash
cp .env.local.example .env.local
```

`.env.local`の内容：
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. 開発サーバーの起動

```bash
npm run dev
```

アプリケーションが起動したら、http://localhost:3000 にアクセスできます。

## バックエンドとの連携

このフロントエンドは、FastAPIで構築されたバックエンドAPIと連携します。

### バックエンドの起動

フロントエンドを使用する前に、バックエンドAPIサーバーを起動してください：

```bash
cd ../backend
python start_server.py
```

バックエンドは http://localhost:8000 で起動します。

## 機能

### ゲームモード

1. **対人戦モード**: 2人のプレイヤーが交互に手を打つ
2. **vsバックエンドAI**: バックエンドのランダムAIと対戦

### ゲームの遊び方

1. ゲームモードを選択
2. 盤面をクリックして手を配置
3. 3マス以上配置したら「確定」ボタンで手を確定
4. 橋を完成させたプレイヤーの勝ち

### ルール

- **水色プレイヤー**: 上端から下端まで繋ぐ
- **ピンクプレイヤー**: 左端から右端まで繋ぐ
- **ブロック**: 3マス（無限）、4マス（1個）、5マス（1個）
- **配置**: 一直線に配置する
- **2層構造**: レイヤー1とレイヤー2があり、橋渡しが可能

## ディレクトリ構造

```
frontend/
├── app/
│   ├── globals.css      # グローバルスタイル
│   ├── layout.tsx       # レイアウトコンポーネント
│   └── page.tsx         # メインページ（ゲーム画面）
├── components/
│   └── Board.tsx        # 盤面コンポーネント（未使用）
├── lib/
│   └── api-client.ts    # APIクライアント
├── types/
│   └── game.ts          # 型定義
├── public/              # 静的ファイル
├── .env.local           # 環境変数（ローカル）
├── .env.local.example   # 環境変数のサンプル
├── next.config.ts       # Next.js設定
├── tailwind.config.ts   # Tailwind CSS設定
├── tsconfig.json        # TypeScript設定
├── package.json         # 依存関係
└── README.md            # このファイル
```

## 開発

### ビルド

```bash
npm run build
```

### 本番環境での起動

```bash
npm start
```

### Lintチェック

```bash
npm run lint
```

## API連携

フロントエンドは以下のAPIエンドポイントを使用します：

- `POST /api/game/new` - 新しいゲームを作成
- `GET /api/game/{game_id}/state` - ゲーム状態を取得
- `POST /api/game/move` - 手を適用
- `POST /api/ai/move` - AIの手を取得
- `POST /api/game/{game_id}/reset` - ゲームをリセット
- `GET /health` - ヘルスチェック

詳細は `lib/api-client.ts` を参照してください。

## トラブルシューティング

### APIサーバーに接続できない

1. バックエンドAPIサーバーが起動しているか確認
2. `.env.local`の`NEXT_PUBLIC_API_URL`が正しいか確認
3. CORSエラーの場合、バックエンドのCORS設定を確認

### ゲームが動作しない

1. ブラウザのコンソールでエラーを確認
2. バックエンドのログを確認
3. ページをリロードして再試行

## 今後の実装予定

- [ ] ゲーム履歴の表示
- [ ] 手の取り消し機能（UI）
- [ ] 合法手のハイライト表示
- [ ] アニメーション効果
- [ ] ユーザー認証
- [ ] オンライン対戦
- [ ] 棋譜の保存・読み込み

## ライセンス

このプロジェクトは個人開発用です。
