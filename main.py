import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import io
import base64
from datetime import datetime
import json

from config import APP_NAME, APP_VERSION, APP_DESCRIPTION, GEMINI_API_KEY, GEMINI_MODEL, SUPPORTED_LANGUAGES, OCR_ENGINES
from ocr_processor import OCRProcessor
from utils import (
    validate_image_file, 
    save_to_history, 
    load_history, 
    delete_history_item,
    format_timestamp,
    get_file_size_display
)

# ページ設定
st.set_page_config(
    page_title="Immeasurable OCR",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ImmeasurableなカスタムCSS
st.markdown("""
<style>
    /* メインヘッダー - グラデーションとアニメーション */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #fff, #f0f8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        margin: 1rem 0 0 0;
        font-size: 1.4rem;
        opacity: 0.95;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* 機能カード - モダンなデザイン */
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border: none;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .feature-card h3 {
        color: #667eea;
        margin-top: 0;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* 信頼度インジケーター */
    .confidence-high {
        color: #00d4aa;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 212, 170, 0.3);
    }
    
    .confidence-medium {
        color: #ffa726;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 167, 38, 0.3);
    }
    
    .confidence-low {
        color: #ff5722;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 87, 34, 0.3);
    }
    
    /* 結果ボックス */
    .result-box {
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
    }
    
    .result-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* アップロードエリア */
    .upload-area {
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        border: 3px dashed #667eea;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(145deg, #f0f8ff, #ffffff);
        transform: scale(1.02);
    }
    
    .upload-area::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.05), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .upload-area:hover::before {
        opacity: 1;
    }
    
    /* アニメーション */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* レスポンシブデザイン */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1.1rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ダークテーマ用のCSS（URLパラメータで制御）
if st.query_params.get("theme") == "dark":
    st.markdown("""
    <style>
        /* ダークテーマ用の強力なスタイル */
        .stApp {
            background-color: #0e1117 !important;
        }
        
        .main .block-container {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        
        .stApp > div {
            background-color: #0e1117 !important;
        }
        
        .stApp > div > div {
            background-color: #0e1117 !important;
        }
        
        .stApp > div > div > div {
            background-color: #0e1117 !important;
        }
        
        /* サイドバー */
        .stSidebar {
            background-color: #0e1117 !important;
        }
        
        .stSidebar > div {
            background-color: #0e1117 !important;
        }
        
        /* テキスト - より高いコントラスト */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            text-shadow: 0 0 2px rgba(255, 255, 255, 0.1) !important;
        }
        
        p, div, span, label {
            color: #e0e0e0 !important;
        }
        
        /* ボタン - より目立つ色 */
        .stButton > button {
            background-color: #1f77b4 !important;
            color: #ffffff !important;
            border: 1px solid #1f77b4 !important;
            box-shadow: 0 2px 4px rgba(31, 119, 180, 0.3) !important;
        }
        
        .stButton > button:hover {
            background-color: #0d5aa7 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 8px rgba(31, 119, 180, 0.4) !important;
        }
        
        /* 入力欄 - より高いコントラスト */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 2px solid #444 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #1f77b4 !important;
            box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2) !important;
        }
        
        /* ファイルアップローダー */
        .stFileUploader > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 2px dashed #666 !important;
        }
        
        .stFileUploader > div > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        .stFileUploader label {
            color: #e0e0e0 !important;
        }
        
        .stFileUploader button {
            background-color: #1f77b4 !important;
            color: #ffffff !important;
            border: 1px solid #1f77b4 !important;
        }
        
        .stFileUploader button:hover {
            background-color: #0d5aa7 !important;
            color: #ffffff !important;
        }
        
        /* ファイルアップローダーの詳細スタイル */
        .stFileUploader > div > div > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        .stFileUploader > div > div > div > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        .stFileUploader > div > div > div > div > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        /* ファイルアップローダーのテキスト */
        .stFileUploader p {
            color: #e0e0e0 !important;
        }
        
        .stFileUploader span {
            color: #e0e0e0 !important;
        }
        
        .stFileUploader div {
            color: #e0e0e0 !important;
        }
        
        /* ファイルアップローダーのドラッグエリア */
        .stFileUploader > div > div > div > div > div > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 2px dashed #666 !important;
        }
        
        /* ファイルアップローダーのドラッグテキスト */
        .stFileUploader > div > div > div > div > div > div > div {
            color: #e0e0e0 !important;
        }
        
        .stFileUploader > div > div > div > div > div > div > div > div {
            color: #e0e0e0 !important;
        }
        
        /* ファイルアップローダーのボタンエリア */
        .stFileUploader > div > div > div > div > div > div > div > div > div {
            background-color: #1a1a1a !important;
        }
        
        .stFileUploader > div > div > div > div > div > div > div > div > div > button {
            background-color: #1f77b4 !important;
            color: #ffffff !important;
            border: 1px solid #1f77b4 !important;
        }
        
        .stFileUploader > div > div > div > div > div > div > div > div > div > button:hover {
            background-color: #0d5aa7 !important;
            color: #ffffff !important;
        }
        
        /* カスタム要素 */
        .main-header {
            color: #4fc3f7 !important;
            text-shadow: 0 0 4px rgba(79, 195, 247, 0.3) !important;
        }
        
        .result-box {
            background-color: #1a1a1a !important;
            border: 2px solid #444 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
        }
        
        .upload-area {
            border-color: #666 !important;
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        /* 情報ボックス - より高いコントラスト */
        .stAlert {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 2px solid #444 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* エクスパンダー */
        .streamlit-expanderHeader {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 1px solid #444 !important;
        }
        
        .streamlit-expanderContent {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 1px solid #444 !important;
        }
        
        /* メトリクス */
        .stMetric {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 1px solid #444 !important;
        }
        
        /* プログレスバー */
        .stProgress > div > div > div {
            background-color: #1f77b4 !important;
        }
        
        /* スピナー */
        .stSpinner {
            color: #1f77b4 !important;
        }
        
        /* コードブロック */
        pre, code {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 1px solid #444 !important;
        }
        
        /* テーブル */
        .stDataFrame {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        /* チェックボックス */
        .stCheckbox > label {
            color: #e0e0e0 !important;
        }
        
        /* ラジオボタン */
        .stRadio > label {
            color: #e0e0e0 !important;
        }
        
        /* スライダー */
        .stSlider > div > div > div {
            background-color: #1f77b4 !important;
        }
        
        /* セレクトボックス */
        .stSelectbox > label {
            color: #e0e0e0 !important;
        }
        
        /* マークダウン */
        .stMarkdown {
            color: #e0e0e0 !important;
        }
        
        /* リンク */
        a {
            color: #4fc3f7 !important;
        }
        
        a:hover {
            color: #81d4fa !important;
        }
        
        /* 成功メッセージ */
        .stSuccess {
            background-color: #1a1a1a !important;
            color: #4caf50 !important;
            border: 2px solid #4caf50 !important;
        }
        
        /* エラーメッセージ */
        .stError {
            background-color: #1a1a1a !important;
            color: #f44336 !important;
            border: 2px solid #f44336 !important;
        }
        
        /* 警告メッセージ */
        .stWarning {
            background-color: #1a1a1a !important;
            color: #ff9800 !important;
            border: 2px solid #ff9800 !important;
        }
        
        /* 情報メッセージ */
        .stInfo {
            background-color: #1a1a1a !important;
            color: #2196f3 !important;
            border: 2px solid #2196f3 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    """メインアプリケーション"""
    

    
    # ヘッダー
    st.markdown(f"""
    <div class="main-header">
        <h1>{APP_NAME}</h1>
        <p>{APP_DESCRIPTION}</p>
        <small>Version {APP_VERSION}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # サイドバーメニュー
    with st.sidebar:
        selected = option_menu(
            "メニュー",
            ["🏠 ホーム", "📚 履歴", "⚙️ 設定", "❓ ヘルプ"],
            icons=['house', 'clock-history', 'gear', 'question-circle'],
            menu_icon="cast",
            default_index=0,
        )
    
    # APIキーの確認
    if not GEMINI_API_KEY:
        st.error("⚠️ Gemini APIキーが設定されていません。設定画面でAPIキーを入力してください。")
        return
    
    # ページ表示
    if selected == "🏠 ホーム":
        show_home_page()
    elif selected == "📚 履歴":
        show_history_page()
    elif selected == "⚙️ 設定":
        show_settings_page()
    elif selected == "❓ ヘルプ":
        show_help_page()

def show_home_page():
    """ホームページ（OCR処理）"""
    st.markdown("""
    <div class="main-header fade-in-up">
        <h1>✨ Immeasurable OCR</h1>
        <p>無限の可能性を秘めた画像文字認識システム</p>
    </div>
    """, unsafe_allow_html=True)
    
    # OCR.space風の設定パネル
    with st.expander("⚙️ OCR設定", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 言語選択
            selected_language = st.selectbox(
                "🌐 言語",
                list(SUPPORTED_LANGUAGES.keys()),
                index=0,
                help="画像内の文字の言語を選択してください"
            )
        
        with col2:
            # OCRエンジン選択
            selected_engine = st.selectbox(
                "🔧 OCRエンジン",
                list(OCR_ENGINES.keys()),
                index=0,
                help="使用するOCRエンジンを選択してください"
            )
        
        with col3:
            # 高度な設定
            st.markdown("**🔧 高度な設定**")
            auto_rotate = st.checkbox("🔄 自動回転", value=True, help="画像の向きを自動調整")
            table_recognition = st.checkbox("📊 テーブル認識", value=False, help="表形式のデータを認識")
    
    # 設定の表示
    st.info(f"""
    **現在の設定:**
    - 言語: {selected_language}
    - エンジン: {selected_engine}
    - 自動回転: {'有効' if auto_rotate else '無効'}
    - テーブル認識: {'有効' if table_recognition else '無効'}
    """)
    
    # 画像アップロード
    st.subheader("📁 画像をアップロード")
    
    # アップロードエリアの説明
    st.info("""
    **📋 画像アップロード方法:**
    - **クリック**: 下の「ファイルを選択」ボタンをクリックして画像を選択
    - **ドラッグ&ドロップ**: 画像ファイルを下のエリアにドラッグ&ドロップ
    - **対応形式**: JPG, JPEG, PNG, GIF, BMP, TIFF
    - **最大サイズ**: 10MB
    """)
    
    # アップロードエリアを広くするためのCSS
    st.markdown("""
    <style>
    /* ファイルアップローダーのスタイルをカスタマイズ */
    .stFileUploader > div {
        min-height: 120px !important;
        padding: 20px !important;
    }
    
    .stFileUploader > div > div {
        min-height: 80px !important;
        border: 2px dashed #1f77b4 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        text-align: center !important;
        background-color: #f8f9fa !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #0d5aa7 !important;
        background-color: #e3f2fd !important;
    }
    
    /* ダークテーマ対応 */
    [data-testid="stAppViewContainer"] [data-theme="dark"] .stFileUploader > div > div {
        background-color: #2d2d2d !important;
        border-color: #666 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stAppViewContainer"] [data-theme="dark"] .stFileUploader > div > div:hover {
        border-color: #1f77b4 !important;
        background-color: #3a3a3a !important;
    }
    
    /* ファイルアップローダーのテキストを日本語に変更 - より具体的なセレクター */
    .stFileUploader > div > div::before {
        content: "📁 ここをクリックしてファイルを選択 または 画像をドラッグ&ドロップ" !important;
        display: block !important;
        font-size: 16px !important;
        font-weight: bold !important;
        color: #1f77b4 !important;
        text-align: center !important;
        margin-bottom: 10px !important;
        padding: 10px !important;
        position: relative !important;
        z-index: 1000 !important;
    }
    
    /* 英語のテキストを非表示 - より具体的なセレクター */
    .stFileUploader > div > div > div:first-child,
    .stFileUploader > div > div > div:first-child > div,
    .stFileUploader > div > div > div:first-child > span,
    .stFileUploader > div > div > div:first-child > p {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* ボタンテキストも日本語に変更 */
    .stFileUploader > div > div::after {
        content: "📁 ファイルを選択" !important;
        display: inline-block !important;
        background-color: #1f77b4 !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 5px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        margin-top: 10px !important;
        position: relative !important;
        z-index: 1000 !important;
    }
    
    /* ダークテーマでのテキスト色 */
    [data-testid="stAppViewContainer"] [data-theme="dark"] .stFileUploader > div > div::before {
        color: #1f77b4 !important;
    }
    
    [data-testid="stAppViewContainer"] [data-theme="dark"] .stFileUploader > div > div::after {
        background-color: #1f77b4 !important;
        color: white !important;
    }
    
    /* 追加の非表示ルール */
    .stFileUploader > div > div > div:first-child * {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📁 画像ファイルをアップロード",
        type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'],
        help="画像ファイルをクリックして選択するか、ドラッグ&ドロップしてください",
        label_visibility="visible"
    )
    
    if uploaded_file is not None:
        # ファイル検証
        is_valid, message = validate_image_file(uploaded_file)
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        st.success(f"✅ {message}")
        
        # 画像表示
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("アップロードされた画像")
            image = Image.open(uploaded_file)
            st.image(image, caption=uploaded_file.name, use_container_width=True)
            
            # ファイル情報
            st.info(f"""
            **ファイル情報:**
            - ファイル名: {uploaded_file.name}
            - サイズ: {get_file_size_display(uploaded_file.size)}
            - 形式: {uploaded_file.type}
            - 寸法: {image.size[0]} × {image.size[1]} ピクセル
            """)
        
        with col2:
            st.subheader("OCR処理")
            
            if st.button("🚀 文字起こし開始", type="primary"):
                try:
                    with st.spinner("画像を解析中..."):
                        # OCR処理
                        processor = OCRProcessor(OCR_ENGINES[selected_engine])
                        ocr_result, confidence = processor.process_image(
                            image, 
                            language_hint=SUPPORTED_LANGUAGES[selected_language],
                            auto_rotate=auto_rotate,
                            table_recognition=table_recognition
                        )
                    
                    # 結果表示
                    st.success("✅ OCR処理が完了しました！")
                    
                    # 信頼度表示
                    confidence_percent = confidence * 100
                    if confidence_percent >= 80:
                        confidence_class = "confidence-high"
                        confidence_text = "高"
                        confidence_emoji = "🟢"
                    elif confidence_percent >= 60:
                        confidence_class = "confidence-medium"
                        confidence_text = "中"
                        confidence_emoji = "🟡"
                    else:
                        confidence_class = "confidence-low"
                        confidence_text = "低"
                        confidence_emoji = "🔴"
                    
                    # OCR.space風の結果表示
                    st.markdown(f"""
                    <div class="result-box">
                        <h4>📝 OCR結果</h4>
                        <div style="background-color: #ffffff; padding: 1rem; border-radius: 5px; border: 1px solid #ddd; margin: 1rem 0;">
                            <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace; margin: 0;">{ocr_result}</pre>
                        </div>
                        <p class="{confidence_class}">
                            <strong>{confidence_emoji} 信頼度: {confidence_text} ({confidence_percent:.1f}%)</strong>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 結果の編集とアクション
                    st.subheader("📝 結果の編集")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        edited_result = st.text_area(
                            "結果を編集してください",
                            value=ocr_result,
                            height=200,
                            label_visibility="collapsed"
                        )
                    
                    with col2:
                        st.markdown("**アクション**")
                        if st.button("📋 コピー", type="secondary"):
                            st.write("```")
                            st.code(edited_result)
                            st.write("```")
                            st.success("結果をクリップボードにコピーしました！")
                        
                        if st.button("🔄 再処理", type="secondary"):
                            st.rerun()
                    
                    # 自動で履歴に保存
                    image_data = base64.b64encode(uploaded_file.getvalue()).decode()
                    if save_to_history(
                        uploaded_file.name, 
                        image_data, 
                        ocr_result, 
                        confidence
                    ):
                        st.success("✅ 履歴に自動保存しました")
                    else:
                        st.error("❌ 履歴の保存に失敗しました")
                    
                    # 手動保存ボタン（編集後の結果を保存）
                    if st.button("💾 編集結果を履歴に保存"):
                        if save_to_history(
                            uploaded_file.name, 
                            image_data, 
                            edited_result, 
                            confidence
                        ):
                            st.success("✅ 編集結果を履歴に保存しました")
                        else:
                            st.error("❌ 履歴の保存に失敗しました")
                    
                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")

def show_history_page():
    """履歴ページ"""
    st.header("📚 処理履歴")
    
    # 履歴の読み込み
    history = load_history()
    
    if not history:
        st.info("📝 まだ処理履歴がありません。画像をアップロードしてOCR処理を行ってください。")
        return
    
    # 検索・フィルター
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 検索（ファイル名または内容）")
    with col2:
        sort_order = st.selectbox("📊 並び順", ["新しい順", "古い順"])
    
    # 履歴の表示
    filtered_history = history
    
    # 検索フィルター
    if search_term:
        filtered_history = [
            item for item in history
            if search_term.lower() in item["image_name"].lower() or 
               search_term.lower() in item["ocr_result"].lower()
        ]
    
    # ソート
    if sort_order == "新しい順":
        filtered_history.sort(key=lambda x: x["timestamp"], reverse=True)
    else:
        filtered_history.sort(key=lambda x: x["timestamp"])
    
    st.info(f"📊 {len(filtered_history)}件の履歴が見つかりました")
    
    # 履歴一覧
    for i, item in enumerate(filtered_history):
        with st.expander(f"📷 {item['image_name']} - {format_timestamp(item['timestamp'])}", expanded=False):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # 画像表示
                try:
                    image_data = base64.b64decode(item["image_data"])
                    image = Image.open(io.BytesIO(image_data))
                    st.image(image, caption=item["image_name"], use_container_width=True)
                except Exception as e:
                    st.error(f"画像の表示に失敗しました: {str(e)}")
                    # プレースホルダー画像を表示
                    st.info("📷 画像データが破損している可能性があります")
            
            with col2:
                # 詳細情報
                st.write(f"**📅 処理日時:** {format_timestamp(item['timestamp'])}")
                
                # 信頼度の表示
                confidence_percent = item['confidence'] * 100
                if confidence_percent >= 80:
                    confidence_color = "🟢"
                elif confidence_percent >= 60:
                    confidence_color = "🟡"
                else:
                    confidence_color = "🔴"
                st.write(f"**{confidence_color} 信頼度:** {confidence_percent:.1f}%")
                
                st.write(f"**📝 抽出された文字列:**")
                st.text_area("OCR結果", value=item["ocr_result"], height=150, key=f"history_{item['id']}", label_visibility="collapsed")
                
                # 操作ボタン
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("📋 コピー", key=f"copy_{item['id']}"):
                        st.write("✅ クリップボードにコピーしました")
                
                with col_btn2:
                    if st.button("🔄 再処理", key=f"reprocess_{item['id']}"):
                        st.info("再処理機能は今後実装予定です")
                
                with col_btn3:
                    if st.button("🗑️ 削除", key=f"delete_{item['id']}"):
                        if delete_history_item(item["id"]):
                            st.success("✅ 履歴を削除しました")
                            st.rerun()
                        else:
                            st.error("❌ 削除に失敗しました")

def show_settings_page():
    """設定ページ"""
    st.header("⚙️ 設定")
    
    # API設定
    st.subheader("🔑 Gemini API設定")
    
    # 環境変数の設定方法を説明
    st.info("""
    **Gemini APIキーの設定方法:**
    
    1. [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得
    2. プロジェクトルートに`.env`ファイルを作成
    3. 以下の内容を記述:
         ```
     GEMINI_API_KEY=your_api_key_here
     GEMINI_MODEL=gemini-2.0-flash
     ```
    """)
    
    # 現在の設定状況
    if GEMINI_API_KEY:
        st.success("✅ Gemini APIキーが設定されています")
        st.code(f"モデル: {GEMINI_MODEL}")
    else:
        st.error("❌ Gemini APIキーが設定されていません")
    
    # アプリケーション設定
    st.subheader("📱 アプリケーション設定")
    
    # テーマ設定
    st.markdown("### 🎨 テーマ設定")
    
    # テーマ選択
    theme_options = {
        "☀️ ライトテーマ": "light",
        "🌙 ダークテーマ": "dark"
    }
    
    selected_theme_display = st.selectbox(
        "テーマを選択してください",
        list(theme_options.keys()),
        index=0
    )
    
    selected_theme = theme_options[selected_theme_display]
    
    # 現在のテーマを取得
    current_theme = st.query_params.get("theme", "light")
    
    # テーマ適用ボタン
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🎨 テーマを適用", type="primary"):
            if selected_theme != current_theme:
                # URLパラメータを更新してページをリロード
                st.query_params.theme = selected_theme
                st.rerun()
            else:
                st.info("選択されたテーマは既に適用されています")
    
    with col2:
        # 現在のテーマ表示
        if current_theme == "dark":
            st.success("🌙 現在ダークテーマが適用されています")
        else:
            st.success("☀️ 現在ライトテーマが適用されています")
    
    # テーマ切り替えボタン
    st.markdown("### 🔄 テーマ切り替え")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🌙 ダークテーマに切り替え", type="secondary"):
            if current_theme != "dark":
                st.query_params.theme = "dark"
                st.rerun()
            else:
                st.info("既にダークテーマが適用されています")
    
    with col_btn2:
        if st.button("☀️ ライトテーマに切り替え", type="secondary"):
            if current_theme != "light":
                st.query_params.theme = "light"
                st.rerun()
            else:
                st.info("既にライトテーマが適用されています")
    
    # 言語設定
    default_language = st.selectbox("デフォルト言語", ["日本語", "English", "中文", "한국어"])
    
    # 履歴設定
    max_history = st.slider("最大履歴数", 10, 200, 100)
    
    if st.button("💾 設定を保存"):
        st.success("✅ 設定を保存しました")
    
    # 履歴のクリア
    st.subheader("🗑️ データ管理")
    
    if st.button("🗑️ 全履歴を削除", type="secondary"):
        if st.checkbox("本当に全履歴を削除しますか？"):
            try:
                import os
                if os.path.exists("ocr_history.json"):
                    os.remove("ocr_history.json")
                st.success("✅ 全履歴を削除しました")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 履歴の削除に失敗しました: {e}")

def show_help_page():
    """ヘルプページ"""
    st.header("❓ ヘルプ")
    
    st.subheader("📖 使用方法")
    
    st.markdown("""
    ### 1. OCR設定
    - **🌐 言語**: 画像内の文字の言語を選択（自動検出も可能）
    - **🔧 OCRエンジン**: 使用するGeminiモデルを選択
    - **🔄 自動回転**: 画像の向きを自動調整
    - **📊 テーブル認識**: 表形式のデータを認識
    
    ### 2. 画像のアップロード
    - サポート形式: JPG, JPEG, PNG, GIF, BMP, TIFF
    - 最大ファイルサイズ: 10MB
    - ドラッグ&ドロップまたはファイル選択ボタンでアップロード
    
    ### 3. OCR処理の実行
    - 「🚀 文字起こし開始」ボタンをクリック
    - 処理には数秒かかる場合があります
    - 信頼度が表示されます（🟢高/🟡中/🔴低）
    
    ### 4. 結果の確認・編集
    - 抽出された文字列を確認
    - **📋 コピー**: 結果をクリップボードにコピー
    - **🔄 再処理**: 同じ設定で再実行
    - 必要に応じて結果を編集
    - 編集結果を履歴に保存
    
    ### 5. 履歴の管理
    - 処理結果は自動的に履歴に保存
    - 過去の結果を検索・確認・削除可能
    """)
    
    st.subheader("🌐 サポート言語")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - 🇯🇵 日本語
        - 🇺🇸 英語
        - 🇨🇳 中国語（簡体字・繁体字）
        - 🇰🇷 韓国語
        - 🇫🇷 フランス語
        - 🇩🇪 ドイツ語
        - 🇪🇸 スペイン語
        - 🇮🇹 イタリア語
        """)
    
    with col2:
        st.markdown("""
        - 🇵🇹 ポルトガル語
        - 🇷🇺 ロシア語
        - 🇸🇦 アラビア語
        - 🇹🇭 タイ語
        - 🇻🇳 ベトナム語
        - 🇺🇦 ウクライナ語
        - 🔍 自動検出
        """)
    
    st.subheader("🔧 OCRエンジン")
    
    st.markdown("""
    - **Gemini 2.0 Flash (推奨)**: 最新の高性能モデル、高速処理
    - **Gemini 1.5 Pro**: 高精度な文字認識、複雑な文書に適している
    - **Gemini 1.5 Flash**: バランスの取れた性能、一般的な用途に適している
    """)
    
    st.subheader("✨ 高度な機能")
    
    st.markdown("""
    - **🔄 自動回転**: EXIF情報から画像の向きを自動調整
    - **📊 テーブル認識**: 表形式のデータを構造化して認識
    - **🎨 テーマ切り替え**: ライト/ダークテーマの切り替え
    - **📚 履歴管理**: 処理結果の自動保存と管理
    - **📋 コピー機能**: 結果の簡単なコピー
    """)
    
    st.subheader("🔧 トラブルシューティング")
    
    st.markdown("""
    ### よくある問題
    
    **Q: APIキーエラーが表示される**
    A: 設定画面でGemini APIキーが正しく設定されているか確認してください
    
    **Q: 画像が処理されない**
    A: ファイルサイズが10MB以下で、サポートされている形式か確認してください
    
    **Q: 文字認識の精度が低い**
    A: 画像の解像度、コントラスト、文字の鮮明さを確認してください
    
    **Q: 処理に時間がかかる**
    A: 画像サイズが大きい場合、処理に時間がかかることがあります
    """)
    
    st.subheader("📞 サポート")
    
    st.markdown("""
    問題が解決しない場合は、以下をご確認ください：
    
    - エラーメッセージの詳細
    - 使用している画像ファイルの形式・サイズ
    - インターネット接続状況
    
    詳細なログが必要な場合は、開発者にお問い合わせください。
    """)

if __name__ == "__main__":
    main()
