from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.models import Note, Exam
from app.services import summarize
from app.utils import login_required

note_bp = Blueprint('notes', __name__, url_prefix='/notes')


@note_bp.route('/', methods=['GET'])
@login_required
def list_notes():
    """顯示當前使用者的所有筆記列表（最新在前）。"""
    user_id = session['user_id']
    notes   = Note.get_by_user(user_id)
    return render_template('notes/list.html', notes=notes)


@note_bp.route('/new', methods=['GET'])
@login_required
def new_note():
    """顯示新增筆記頁面（含文字輸入區與語音錄音按鈕）。"""
    return render_template('notes/new.html')


@note_bp.route('/upload', methods=['POST'])
@login_required
def upload_note():
    """
    接收新增筆記表單，交由 AI 整理並儲存。

    表單欄位：
        title       — 筆記標題（必填）
        raw_content — 原始筆記文字（必填）

    流程：
        1. 驗證欄位不為空
        2. 呼叫 ai_service.summarize() 取得 AI 摘要
        3. Note.create() 寫入資料庫
        4. redirect 至筆記詳情頁
    """
    user_id     = session['user_id']
    title       = request.form.get('title', '').strip()
    raw_content = request.form.get('raw_content', '').strip()

    # —— 輸入驗證 ——
    if not raw_content:
        flash('請輸入筆記內容', 'danger')
        return redirect(url_for('notes.new_note'))

    if not title:
        title = raw_content[:40] + ('...' if len(raw_content) > 40 else '')

    # —— 呼叫 AI 整理摘要 ——
    summary = summarize(raw_content)
    if not summary:
        flash('AI 整理服務暫時無法使用，已儲存原始筆記。', 'warning')

    # —— 儲存筆記 ——
    note = Note.create(
        user_id=user_id,
        title=title,
        raw_content=raw_content,
        summary=summary if summary else None
    )

    if note is None:
        flash('筆記儲存失敗，請稍後再試', 'danger')
        return redirect(url_for('notes.new_note'))

    flash('筆記已成功整理並儲存！', 'success')
    return redirect(url_for('notes.view_note', note_id=note.id))


@note_bp.route('/<int:note_id>', methods=['GET'])
@login_required
def view_note(note_id):
    """
    顯示單一筆記的整理內容與歷史測驗紀錄。

    URL 參數：
        note_id — 筆記主鍵

    錯誤：
        404 — 筆記不存在
        403 — 不是本人的筆記
    """
    note = Note.get_by_id(note_id)
    if note is None:
        abort(404)
    if note.user_id != session['user_id']:
        abort(403)

    exams = Exam.get_by_note(note_id)
    return render_template('notes/view.html', note=note, exams=exams)


@note_bp.route('/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """
    刪除指定筆記（關聯測驗 CASCADE 刪除）。

    URL 參數：
        note_id — 筆記主鍵

    錯誤：
        404 — 筆記不存在
        403 — 不是本人的筆記
    """
    note = Note.get_by_id(note_id)
    if note is None:
        abort(404)
    if note.user_id != session['user_id']:
        abort(403)

    success = note.delete()
    if success:
        flash('筆記已成功刪除', 'success')
    else:
        flash('刪除失敗，請稍後再試', 'danger')

    return redirect(url_for('notes.list_notes'))
