# リスマ（LisMa）- BtoB営業支援のためのリスト作成アプリ

リスマ（LisMa）は、BtoB営業支援のためのリスト作成アプリケーションです。Web上に散在する企業情報を自動収集し、営業リストを効率的に作成・管理できます。

## 主な機能

### リスタ（ListA）- リスト作成機能
- キーワード検索：指定したキーワードを含む企業を検索
- 業種×住所検索：業種と地域を指定して企業を検索
- Web全体検索：様々なポータルサイトや電話帳サイトから情報収集

### リスツール（Listool）- リスト整理機能
- データ前処理：スペース、タブ、空白行の除去
- 表記の統一：法人格、住所、電話番号などの表記を統一
- 重複削除：既存リストとの重複を自動検出・削除

### リストモット（ListMotto）- リスト情報付加機能
- 企業情報の付加：従業員規模、資本金規模、売上規模などの条件設定
- データエンリッチメント：外部APIと連携した情報付加

## 技術スタック

### バックエンド
- 言語：Python 3.9+
- フレームワーク：FastAPI
- データベース：PostgreSQL
- 認証：JWT、OAuth2、SAML（SSO対応）

### フロントエンド
- 言語：TypeScript
- フレームワーク：React + Next.js
- UIライブラリ：Material-UI

### インフラ
- コンテナ化：Docker
- デプロイ：Render

## 開発環境のセットアップ

### 前提条件
- Python 3.9以上
- Node.js 14以上
- PostgreSQL

### バックエンドのセットアップ
```bash
# リポジトリのクローン
git clone https://github.com/yourusername/risma-project.git
cd risma-project

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な設定を行う

# アプリケーションの起動
cd app
uvicorn main:app --reload
```

### フロントエンドのセットアップ
```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存パッケージのインストール
npm install

# 開発サーバーの起動
npm run dev
```

## デプロイ

### Renderへのデプロイ
1. Renderアカウントを作成
2. 新しいWeb Serviceを作成
3. GitHubリポジトリと連携
4. 環境変数を設定
5. デプロイを実行

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献
プロジェクトへの貢献は大歓迎です。バグ報告、機能リクエスト、プルリクエストなどをお待ちしています。
