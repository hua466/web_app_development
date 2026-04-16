"""
config.py — 全域設定與第三方 API 金鑰。

⚠️ 請勿將此檔案的真實金鑰提交至 Git。
   建議使用 .env 搭配 python-dotenv 載入敏感資料。
"""

import os

# ── Flask 核心設定 ─────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ── AI 服務 API 金鑰 ──────────────────────────────────────────
# 從環境變數讀取，避免明碼寫入程式碼
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# ── AI 出題設定 ────────────────────────────────────────────────
DEFAULT_QUESTION_COUNT = 5   # 每次測驗預設題數
