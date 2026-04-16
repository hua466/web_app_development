from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Note, Exam
from app.utils import login_required

note_bp = Blueprint('notes', __name__, url_prefix='/notes')


@note_bp.route('/', methods=['GET'])
@login_required
def list_notes():
    """
    顯示當前使用者的所有筆記列表。
    - 邏輯：Note.get_by_user(user_id) 取得所有筆記（最新在前）
    - 輸出：渲染 notes/list.html，傳入 notes
    """
    pass


@note_bp.route('/new', methods=['GET'])
@login_required
def new_note():
    """
    顯示新增筆記頁面。
    - 輸出：渲染 notes/new.html
      頁面內含：文字輸入區、語音錄音按鈕（Web Speech API）
    """
    pass


@note_bp.route('/upload', methods=['POST'])
@login_required
def upload_note():
    """
    接收新增筆記表單並交由 AI 整理。
    - 輸入（表單）：title, raw_content
    - 邏輯：
        1. 驗證 raw_content 不為空
        2. 呼叫 ai_service.summarize(raw_content) 取得 AI 摘要
        3. Note.create(user_id, title, raw_content, summary) 儲存
    - 成功：redirect /notes/<note_id>
    - 失敗：
        * 內容為空 → flash '請輸入筆記內容'，redirect /notes/new
        * AI 服務失敗 → flash 警告，以 summary=None 儲存，redirect /notes/<note_id>
    """
    pass


@note_bp.route('/<int:note_id>', methods=['GET'])
@login_required
def view_note(note_id):
    """
    顯示單一筆記的整理內容。
    - 輸入：URL 參數 note_id
    - 邏輯：
        1. Note.get_by_id(note_id) 查詢筆記
        2. 驗證筆記屬於當前使用者
        3. Exam.get_by_note(note_id) 取得歷史測驗
    - 輸出：渲染 notes/view.html，傳入 note, exams
    - 錯誤：
        * 筆記不存在 → abort(404)
        * 非本人筆記 → abort(403)
    """
    pass


@note_bp.route('/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """
    刪除指定筆記（及關聯測驗，CASCADE）。
    - 輸入：URL 參數 note_id
    - 邏輯：
        1. Note.get_by_id(note_id) 查詢並驗證所有權
        2. note.delete()
    - 成功：flash '筆記已刪除'，redirect /notes
    - 錯誤：
        * 筆記不存在 → abort(404)
        * 非本人筆記 → abort(403)
    """
    pass
