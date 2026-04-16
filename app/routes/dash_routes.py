from flask import Blueprint, render_template, session
from app.models import Note, Exam, Answer
from app.utils import login_required

dash_bp = Blueprint('dashboard', __name__)


@dash_bp.route('/')
def index():
    """
    根路徑，redirect 至 /dashboard。
    """
    pass


@dash_bp.route('/dashboard')
@login_required
def dashboard():
    """
    顯示學習儀表板。
    - 從 session 取得 user_id
    - 查詢：
        * Note.get_by_user(user_id)         → 最近 5 筆筆記
        * Exam.get_by_user(user_id)         → 所有測驗紀錄（計算平均成績）
        * Answer.get_wrong_answers(user_id) → 答錯題目（弱點清單）
    - 輸出：渲染 dashboard/index.html
      傳入：recent_notes, exams, avg_score, wrong_count
    """
    pass
