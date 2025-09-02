"""
Vercel用のStreamlitアプリケーションエントリーポイント
"""
import os
import sys

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# main.pyをインポートして実行
if __name__ == "__main__":
    from main import main
    main()
