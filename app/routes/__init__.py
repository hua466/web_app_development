"""
app/routes/__init__.py

統一匯出所有 Blueprint，方便 app/__init__.py 一次 register。
"""

from .auth_routes import auth_bp
from .dash_routes import dash_bp
from .note_routes import note_bp
from .exam_routes import exam_bp

__all__ = ['auth_bp', 'dash_bp', 'note_bp', 'exam_bp']
