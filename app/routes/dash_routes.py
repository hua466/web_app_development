from flask import Blueprint, render_template, redirect, url_for, session
from app.models import Note, Exam, Answer
from app.utils import login_required

dash_bp = Blueprint('dashboard', __name__)


@dash_bp.route('/')
def index():
    """根路徑：已登入 → Dashboard；未登入 → 登入頁。"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))


@dash_bp.route('/dashboard')
@login_required
def dashboard():
    """
    顯示學習儀表板。
    - 最近 5 筆筆記
    - 所有測驗紀錄（並計算平均分數）
    - 答錯題數統計
    """
    user_id = session['user_id']

    recent_notes  = Note.get_by_user(user_id)[:5]
    exams         = Exam.get_by_user(user_id)
    wrong_answers = Answer.get_wrong_answers(user_id)

    # 計算平均答對率
    completed = [e for e in exams if e.score is not None]
    avg_score = (
        round(sum(e.percentage for e in completed) / len(completed), 1)
        if completed else None
    )

    return render_template(
        'dashboard/index.html',
        recent_notes=recent_notes,
        exams=exams,
        avg_score=avg_score,
        wrong_count=len(wrong_answers),
        exam_count=len(completed)
    )
