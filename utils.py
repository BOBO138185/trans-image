import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st
from PIL import Image
import io
import base64

def validate_image_file(file) -> tuple[bool, str]:
    """画像ファイルの検証を行う"""
    if file is None:
        return False, "ファイルが選択されていません"
    
    # ファイルサイズの検証
    if file.size > 10 * 1024 * 1024:  # 10MB
        return False, "ファイルサイズが10MBを超えています"
    
    # ファイル形式の検証
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_extension not in allowed_extensions:
        return False, f"サポートされていないファイル形式です: {file_extension}"
    
    return True, "ファイルが正常です"

def image_to_base64(image: Image.Image) -> str:
    """PIL画像をbase64エンコードされた文字列に変換"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def save_to_history(image_name: str, image_data: str, ocr_result: str, confidence: float = 0.0):
    """OCR結果を履歴に保存"""
    history_file = "ocr_history.json"
    
    # 既存の履歴を読み込み
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    # 新しい履歴項目を追加
    import uuid
    new_item = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "image_name": image_name,
        "image_data": image_data,
        "ocr_result": ocr_result,
        "confidence": confidence
    }
    
    history.append(new_item)
    
    # 履歴の最大数を制限
    if len(history) > 100:
        history = history[-100:]
    
    # 履歴を保存
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"履歴を保存しました: {new_item['id']}")  # デバッグ用
        return True
    except Exception as e:
        print(f"履歴の保存に失敗しました: {e}")  # デバッグ用
        return False

def load_history() -> List[Dict]:
    """履歴を読み込み"""
    history_file = "ocr_history.json"
    
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"履歴の読み込みに失敗しました: {e}")
        return []

def delete_history_item(item_id: int) -> bool:
    """履歴項目を削除"""
    history = load_history()
    history = [item for item in history if item["id"] != item_id]
    
    try:
        with open("ocr_history.json", 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"履歴の削除に失敗しました: {e}")
        return False

def format_timestamp(timestamp_str: str) -> str:
    """タイムスタンプを読みやすい形式に変換"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y年%m月%d日 %H:%M:%S")
    except:
        return timestamp_str

def get_file_size_display(size_bytes: int) -> str:
    """ファイルサイズを読みやすい形式に変換"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
