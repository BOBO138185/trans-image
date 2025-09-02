import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Google Gemini API設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# アプリケーション設定
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB in bytes
SUPPORTED_FORMATS = os.getenv("SUPPORTED_FORMATS", "jpg,jpeg,png,gif,bmp,tiff").split(",")

# OCR設定
SUPPORTED_LANGUAGES = {
    "自動検出": "auto",
    "日本語": "japanese",
    "英語": "english", 
    "中国語（簡体字）": "chinese_simplified",
    "中国語（繁体字）": "chinese_traditional",
    "韓国語": "korean",
    "フランス語": "french",
    "ドイツ語": "german",
    "スペイン語": "spanish",
    "イタリア語": "italian",
    "ポルトガル語": "portuguese",
    "ロシア語": "russian",
    "アラビア語": "arabic",
    "タイ語": "thai",
    "ベトナム語": "vietnamese",
    "ウクライナ語": "ukrainian"
}

OCR_ENGINES = {
    "Gemini 2.0 Flash (推奨)": "gemini-2.0-flash",
    "Gemini 1.5 Pro": "gemini-1.5-pro", 
    "Gemini 1.5 Flash": "gemini-1.5-flash"
}

# アプリケーション情報
APP_NAME = "画像OCR Webサイト"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "画像内の文字列をGoogle Gemini APIで文字起こしするWebアプリケーション"

# 履歴保存設定
HISTORY_FILE = "ocr_history.json"
MAX_HISTORY_ITEMS = 100
