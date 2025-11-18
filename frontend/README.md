# ワタルート道場 - フロントエンド

Next.js + React + TypeScript で構築されたワタルートゲームのフロントエンドです。

## 構成

- **Next.js 16**: React フレームワーク
- **React 19**: UI ライブラリ
- **TypeScript**: 型安全性
- **Tailwind CSS 4**: スタイリング

## セットアップ

```bash
# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開いてください。

## ディレクトリ構造

```
frontend/
├── app/              # Next.js App Router
│   ├── page.tsx      # メインページ
│   ├── layout.tsx    # レイアウト
│   └── globals.css   # グローバルスタイル
├── components/       # Reactコンポーネント
│   └── Board.tsx     # 盤面描画コンポーネント
└── public/           # 静的ファイル
```

## 機能

### 現在実装済み
- 18×18の盤面描画
- レイヤー1/レイヤー2の表示
- プレイヤー情報の表示（ブロック残数など）

### 今後実装予定
- バックエンドAPIとの連携
- リアルタイム対戦機能
- ゲームロジックの統合

## バックエンドとの連携

バックエンドAPIは別途 `backend/` ディレクトリで Python (FastAPI) として実装されます。
フロントエンドはAPIを通じてゲーム状態を取得・更新します。

## デプロイ

Vercelへのデプロイを想定しています：

```bash
npm run build
```

