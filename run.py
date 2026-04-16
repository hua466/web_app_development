"""
run.py — 系統進入點，啟動 Flask 開發伺服器。
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
