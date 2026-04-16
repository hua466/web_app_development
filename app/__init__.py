"""
app/__init__.py

Flask Application Factory — 初始化 Flask app、資料庫與所有 Blueprint。
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# 自動載入專案根目錄的 .env 檔案（若存在）
load_dotenv()

# 建立全域 db 物件（在 models 中 import 使用）
db = SQLAlchemy()


def create_app(config=None):
    """
    Application Factory。
    - 初始化 Flask 與 SQLAlchemy
    - 載入設定（config.py 或傳入的 dict）
    - 匯入並注冊所有 Blueprint
    - 建立資料庫資料表（若不存在）
    - 回傳 app 實例
    """
    app = Flask(__name__, instance_relative_config=True)

    # ── 預設設定 ──────────────────────────────────────────────
    app.config['SECRET_KEY'] = 'change-me-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 允許外部傳入設定覆蓋預設值
    if config:
        app.config.update(config)

    # ── 初始化擴充套件 ─────────────────────────────────────────
    db.init_app(app)

    # ── 注冊 Blueprint ────────────────────────────────────────
    from app.routes import auth_bp, dash_bp, note_bp, exam_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(note_bp)
    app.register_blueprint(exam_bp)

    # ── 建立資料表 ────────────────────────────────────────────
    with app.app_context():
        from app.models import User, Note, Exam, Question, Answer  # noqa: F401
        db.create_all()

    return app
