# YouTube トレンド分析システム

FlaskベースのWebアプリケーションで、Google Gemini AIを活用してYouTubeのトレンド分析とコンテンツスクリプトの最適化生成を行います。このシステムは、コンテンツクリエイター向けに包括的なトレンド分析、文字起こし処理、AI駆動のスクリプト生成を提供します。

## 主な機能

- 🔍 **高度なYouTube検索**: アップロード日時、動画の長さ、並び替え設定によるフィルタリング
- 📊 **トレンド分析**: 人気コンテンツのパターンとエンゲージメント指標の分析
- 📝 **文字起こし処理**: 動画の自動文字起こしと処理
- 🤖 **AIスクリプト生成**: Gemini AIを使用した最適化されたコンテンツスクリプトの生成
- 🖼️ **インタラクティブUI**: 動的なサムネイルプレビューとホバーエフェクト
- 🌏 **日本語対応**: 完全な日本語サポート

## 技術スタック

- **バックエンド**: Python 3.11, Flask
- **フロントエンド**: JavaScript, Bootstrap 5
- **AI統合**: Google Gemini API
- **データ処理**: BeautifulSoup4, Selenium
- **動画処理**: YouTube Transcript API
- **スタイリング**: Bootstrap Dark ThemeによるカスタムCSS

## 前提条件

- Python 3.11以上
- Google Gemini APIキー
- YouTubeデータ取得用のインターネット接続

## セットアップ

1. Gitコマンドの導入

下記URLからインストール

https://git-scm.com/downloads


2. 環境変数の設定:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```
.env.templateをコピーして.envを作成し、上記のAPIキーを設定

FLASK_SECRET_KEYは適当な文字列を設定でいいので、このままで良いです。
GEMINI_API_KEYはGoogle ai Studioで取得したAPIキーを設定します。

GEMINI_API_KEYは詳しくはこちら
https://note.com/tacyan/n/n520495acc736

Gitを導入出来たら、以下のコマンドでリポジトリをクローンします。

入れたいディレクトリに移動してから以下のコマンドを実行して下さい。

```
git clone https://github.com/tacyan/YouTube-Trend.git
```

gitの導入が難しいのであれば、zipファイルでダウンロードして解凍して下さい。

Pythonを導入しているなら、requirements.txtをインストールします。

```
pip install -r requirements.txt
```

Pythonが導入されていないなら、以下のページでインストールします。

https://www.python.org/downloads/

PATHを通しておくと便利です。
PATHを通す所にチェックを入れてインストールして下さい。

gitとpythonの導入が完了したら、以下のコマンドで実行します。

## 実行方法
```
python app.py     
```

アクセス方法

```
http://localhost:5000/
```

## 使用方法

1. Webインターフェースにアクセス
2. 検索キーワードを入力
3. 検索フィルターを設定:
   - アップロード日時（1時間から1ヶ月）
   - 動画の長さ（短い、中程度、長い）
   - 並び替え設定（関連度、日付、視聴回数、評価）
4. 目標動画時間を設定（1-30分）
5. 「トレンド分析」をクリックしてトレンド分析とコンテンツ生成を実行

## 機能の詳細

### 検索とフィルタリング
- 柔軟な日付範囲フィルタリング
- 動画の長さによるフィルタリング
- 複数の並び替えオプション
- リアルタイム検索結果

### 動画分析
- 高品質なサムネイルプレビュー
- 視聴回数の追跡
- アップロード日時の監視
- チャンネル情報の表示

### 文字起こし処理
- 自動文字起こし抽出
- タイムスタンプ同期
- インタラクティブな文字起こし表示
- コピー機能

### スクリプト生成
- AI駆動のコンテンツ最適化
- 動画時間を考慮したスクリプト生成
- エンゲージメント指標分析
- バイラルトレンドの組み込み

## 開発

プロジェクトはモジュラーアーキテクチャを採用:
- `app.py`: メインのFlaskアプリケーション
- `scraper.py`: YouTubeデータ抽出
- `ai_generator.py`: Gemini AI統合
- `static/`: フロントエンドアセット
- `templates/`: Jinja2テンプレート

## エラーハンドリング

システムには包括的なエラーハンドリングが含まれています:
- APIキーの検証
- YouTube APIのフォールバック
- 文字起こし抽出の冗長性
- ユーザーフレンドリーなエラーメッセージ

## デプロイメント

アプリケーションはReplitでのデプロイメントを想定:
1. リポジトリをフォーク
2. 環境変数を設定
3. Replitのビルトインデプロイメント機能を使用

## コントリビューション

1. リポジトリをフォーク
2. フィーチャーブランチを作成
3. プルリクエストを送信

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。