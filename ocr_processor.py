import base64
import io
from typing import Dict, Optional, Tuple
from PIL import Image
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, SUPPORTED_LANGUAGES, OCR_ENGINES

class OCRProcessor:
    """Google Gemini APIを使用したOCR処理クラス"""
    
    def __init__(self, model_name: str = None):
        """初期化"""
        if not GEMINI_API_KEY:
            raise ValueError("Gemini APIキーが設定されていません")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = model_name or GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)
    
    def process_image(self, image: Image.Image, language_hint: str = "日本語", 
                     auto_rotate: bool = True, table_recognition: bool = False) -> Tuple[str, float]:
        """
        画像をOCR処理して文字列を抽出
        
        Args:
            image: PIL画像オブジェクト
            language_hint: 言語ヒント（例: "日本語", "英語"）
            auto_rotate: 自動回転の有効/無効
            table_recognition: テーブル認識の有効/無効
        
        Returns:
            Tuple[str, float]: (抽出された文字列, 信頼度スコア)
        """
        try:
            # 画像の向きを自動調整
            if auto_rotate:
                image = self._auto_rotate_image(image)
            
            # Gemini API用のプロンプト
            prompt = f"""
            あなたは画像内の文字を正確に読み取るOCR専門家です。
            以下の指示に従って画像内の文字列を抽出してください：
            
            1. 画像内のすべての文字列を正確に読み取る
            2. 文字の順序や配置を保持する
            3. 改行や段落構造を適切に表現する
            4. 手書き文字も可能な限り読み取る
            5. 言語: {language_hint}
            6. 信頼度が低い場合は[信頼度: 低]と明記する
            """
            
            # テーブル認識の指示を追加
            if table_recognition:
                prompt += """
            7. テーブル構造を認識し、表形式で整理する
            8. 列と行の関係を明確に表現する
            """
            
            prompt += f"""
            
            結果は以下の形式で返してください：
            ```
            文字列の内容
            [信頼度: 高/中/低]
            ```
            
            この画像内の文字列を{language_hint}で読み取ってください。
            """
            
            # Gemini APIにリクエスト
            response = self.model.generate_content([prompt, image])
            
            # レスポンスから文字列を抽出
            ocr_text = response.text.strip()
            
            # 信頼度を推定（レスポンス内容から判断）
            confidence = self._estimate_confidence(ocr_text)
            
            # 信頼度の表記を除去して純粋な文字列を取得
            clean_text = self._extract_clean_text(ocr_text)
            
            return clean_text, confidence
            
        except Exception as e:
            if "blocked" in str(e).lower():
                raise Exception("画像の内容がGeminiの安全フィルターによりブロックされました。別の画像を試してください。")
            else:
                raise Exception(f"OCR処理中にエラーが発生しました: {str(e)}")
    
    def _estimate_confidence(self, ocr_text: str) -> float:
        """OCR結果から信頼度を推定"""
        if "[信頼度: 低]" in ocr_text:
            return 0.3
        elif "[信頼度: 中]" in ocr_text:
            return 0.7
        elif "[信頼度: 高]" in ocr_text:
            return 0.9
        else:
            # 文字数や内容から推定
            if len(ocr_text) > 100:
                return 0.8
            elif len(ocr_text) > 50:
                return 0.7
            else:
                return 0.6
    
    def _extract_clean_text(self, ocr_text: str) -> str:
        """信頼度表記を除去して純粋な文字列を取得"""
        # 信頼度の表記を除去
        lines = ocr_text.split('\n')
        clean_lines = []
        
        for line in lines:
            if not any(marker in line for marker in ["[信頼度:", "信頼度:"]):
                clean_lines.append(line)
        
        return '\n'.join(clean_lines).strip()
    
    def _auto_rotate_image(self, image: Image.Image) -> Image.Image:
        """画像の向きを自動調整"""
        try:
            # EXIF情報から回転情報を取得
            if hasattr(image, '_getexif'):
                exif = image._getexif()
                if exif is not None:
                    orientation = exif.get(274)  # Orientation tag
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        except Exception:
            # EXIF情報の取得に失敗した場合は元の画像を返す
            pass
        return image
    
    def get_supported_languages(self) -> Dict[str, str]:
        """サポートされている言語の一覧を取得"""
        return SUPPORTED_LANGUAGES
    
    def get_available_engines(self) -> Dict[str, str]:
        """利用可能なOCRエンジンの一覧を取得"""
        return OCR_ENGINES
    
    def switch_engine(self, engine_name: str):
        """OCRエンジンを切り替え"""
        if engine_name in OCR_ENGINES.values():
            self.model_name = engine_name
            self.model = genai.GenerativeModel(self.model_name)
        else:
            raise ValueError(f"サポートされていないエンジンです: {engine_name}")
