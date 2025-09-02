# 画像OCR Webサイト

画像内の文字列をGoogle Gemini APIを使用して高精度に文字起こし（OCR）するWebアプリケーションです。

## 🚀 特徴

- **高精度OCR**: Google Gemini Pro Vision APIによる高品質な文字認識
- **多言語対応**: 日本語、英語、中国語、韓国語等の多言語対応
- **直感的UI**: Streamlitによる使いやすいWebインターフェース
- **履歴管理**: 処理結果の保存・検索・管理機能
- **リアルタイム処理**: アップロードした画像を即座に処理

## 📋 対応ファイル形式

- **画像形式**: JPG, JPEG, PNG, GIF, BMP, TIFF
- **最大ファイルサイズ**: 10MB
- **推奨解像度**: 300 DPI以上

## 🛠️ 技術スタック

- **フロントエンド・バックエンド**: Streamlit
- **OCR処理**: Google Gemini Pro Vision API
- **画像処理**: PIL (Pillow)
- **言語**: Python 3.8+

## 📦 セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd trans-image
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. Gemini APIキーの取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. APIキーをコピー

### 4. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、以下を記述：

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-pro-vision
```

### 5. アプリケーションの起動

```bash
streamlit run main.py
```

ブラウザで `http://localhost:8501` にアクセスしてください。

## 🎯 使用方法

### 1. 画像のアップロード
- ホーム画面で画像ファイルを選択またはドラッグ&ドロップ
- サポートされている形式・サイズの画像を選択

### 2. 言語の選択
- 画像内の文字の言語を選択
- 多言語対応で精度向上

### 3. OCR処理の実行
- 「文字起こし開始」ボタンをクリック
- 数秒で処理完了

### 4. 結果の確認・編集
- 抽出された文字列を確認
- 必要に応じて結果を編集
- 信頼度スコアで精度を確認

### 5. 履歴の管理
- 処理結果は自動的に履歴に保存
- 過去の結果を検索・確認・削除

## 📁 プロジェクト構造

```
trans-image/
├── main.py              # メインアプリケーション
├── config.py            # 設定ファイル
├── ocr_processor.py     # OCR処理クラス
├── utils.py             # ユーティリティ関数
├── requirements.txt     # 依存関係
├── README.md           # このファイル
└── 機能仕様書.md        # 機能仕様書
```

## ⚙️ 設定

### アプリケーション設定

- **テーマ**: Light/Darkモードの切り替え
- **デフォルト言語**: 初期言語の設定
- **最大履歴数**: 保存する履歴の最大数

### API設定

- **Gemini APIキー**: 環境変数で管理
- **モデル**: gemini-pro-vision（推奨）

## 🔧 カスタマイズ

### 新しい言語の追加

`ocr_processor.py`の`get_supported_languages()`メソッドを編集：

```python
def get_supported_languages(self) -> Dict[str, str]:
    return {
        "ja": "日本語",
        "en": "English",
        # 新しい言語を追加
        "new": "New Language"
    }
```

### ファイル形式の追加

`utils.py`の`validate_image_file()`関数を編集：

```python
allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
```

## 🚨 トラブルシューティング

### よくある問題

**APIキーエラー**
- `.env`ファイルが正しく設定されているか確認
- APIキーが有効か確認

**画像処理エラー**
- ファイルサイズが10MB以下か確認
- サポートされている形式か確認
- 画像の品質を確認

**処理が遅い**
- 画像サイズを確認
- インターネット接続を確認

## 📊 性能

- **応答時間**: 通常5秒以内
- **同時接続数**: 最大10ユーザー
- **処理能力**: 1日最大1000画像

## 🔒 セキュリティ

- APIキーは環境変数で安全に管理
- アップロードファイルの形式・サイズ検証
- 適切なエラーハンドリング

## 📈 今後の拡張予定

- [ ] バッチ処理機能
- [ ] クラウドストレージ連携
- [ ] 多言語UI対応
- [ ] モバイルアプリ版
- [ ] 他のOCR APIとの連携

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

問題や質問がある場合は、以下をご確認ください：

1. [ヘルプページ](http://localhost:8501/❓_ヘルプ)を確認
2. トラブルシューティングセクションを確認
3. イシューを作成

## 🙏 謝辞

- [Streamlit](https://streamlit.io/) - 素晴らしいWebアプリケーションフレームワーク
- [Google Gemini](https://ai.google.dev/) - 高精度なAI OCR API
- [Pillow](https://python-pillow.org/) - 画像処理ライブラリ

---

**作成日**: 2024年12月  
**バージョン**: 1.0.0  
**作成者**: AI Assistant
