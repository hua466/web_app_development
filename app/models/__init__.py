"""
app/models/__init__.py

統一匯出所有 Model，讓 Flask app 初始化時一次 import 並建立所有資料表。
"""

from .user import User
from .note import Note
from .exam import Exam, Question, Answer

__all__ = ['User', 'Note', 'Exam', 'Question', 'Answer']
