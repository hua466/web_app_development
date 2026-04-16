from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Note, Exam, Question, Answer
from app.utils import login_required

exam_bp = Blueprint('exams', __name__, url_prefix='/exams')


@exam_bp.route('/generate/<int:note_id>', methods=['POST'])
@login_required
def generate_exam(note_id):
    """
    根據指定筆記，呼叫 AI 自動出題並建立測驗。
    - 輸入：URL 參數 note_id
    - 邏輯：
        1. Note.get_by_id(note_id) 驗證筆記存在且屬於當前使用者
        2. 確認 note.summary 不為空（需先整理筆記）
        3. 呼叫 ai_service.generate_questions(note.summary) 取得題目 JSON 清單
        4. Exam.create(note_id, user_id, total_questions) 建立測驗紀錄
        5. Question.bulk_create(exam_id, questions) 批次寫入題目
    - 成功：redirect /exams/<exam_id>
    - 錯誤：
        * 筆記不存在 → abort(404)
        * 非本人筆記 → abort(403)
        * 筆記尚未整理（summary 為 None）→ flash '請先整理筆記'，redirect /notes/<note_id>
        * AI 服務失敗 → flash 錯誤訊息，redirect /notes/<note_id>
    """
    pass


@exam_bp.route('/<int:exam_id>', methods=['GET'])
@login_required
def take_exam(exam_id):
    """
    顯示測驗作答頁面。
    - 輸入：URL 參數 exam_id
    - 邏輯：
        1. Exam.get_by_id(exam_id) 取得測驗
        2. 驗證測驗屬於當前使用者
        3. 若 exam.score 已有值（已作答）→ redirect /exams/result/<exam_id>
        4. Question.get_by_exam(exam_id) 取得所有題目
    - 輸出：渲染 exams/take_exam.html，傳入 exam, questions
    - 錯誤：
        * 測驗不存在 → abort(404)
        * 非本人測驗 → abort(403)
    """
    pass


@exam_bp.route('/submit/<int:exam_id>', methods=['POST'])
@login_required
def submit_exam(exam_id):
    """
    送出作答並批改。
    - 輸入（表單）：answer_<question_id> 對應每題答案（'A'~'D'）
    - 邏輯：
        1. 取得 Exam 與 Question 清單並驗證所有權
        2. 遍歷所有題目，比對使用者作答與正確答案，計算 score
        3. Answer.bulk_create(answers_data) 批次儲存作答紀錄
        4. exam.submit(score) 寫入分數與 taken_at
    - 成功：redirect /exams/result/<exam_id>
    - 錯誤：
        * 測驗不存在 → abort(404)
        * 非本人測驗 → abort(403)
        * 已送出過（score 非 None）→ redirect /exams/result/<exam_id>
    """
    pass


@exam_bp.route('/result/<int:exam_id>', methods=['GET'])
@login_required
def exam_result(exam_id):
    """
    顯示測驗成績與 AI 弱點解析。
    - 輸入：URL 參數 exam_id
    - 邏輯：
        1. Exam.get_by_id(exam_id) 驗證存在與所有權
        2. 若 exam.score 為 None（尚未作答）→ redirect /exams/<exam_id>
        3. Answer.get_by_exam(exam_id) 取得所有作答紀錄
        4. 篩選答錯題目 wrong_answers
        5. 若有答錯題目，呼叫 ai_service.analyze_weakness(wrong_questions) 取得建議文字
    - 輸出：渲染 exams/result.html，傳入 exam, answers, wrong_answers, weakness_advice
    - 錯誤：
        * 測驗不存在 → abort(404)
        * 非本人測驗 → abort(403)
    """
    pass
