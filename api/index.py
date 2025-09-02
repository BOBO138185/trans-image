"""
Vercel用のAPIエンドポイント
StreamlitアプリケーションをVercelで動作させるための設定
"""
import os
import sys
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class StreamlitHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Streamlitアプリケーションを起動
        try:
            # main.pyを実行
            from main import main
            main()
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

def handler(request):
    """Vercel用のハンドラー関数"""
    try:
        # Streamlitアプリケーションを起動
        from main import main
        main()
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': 'Streamlit app is running'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': f'Error: {str(e)}'
        }
