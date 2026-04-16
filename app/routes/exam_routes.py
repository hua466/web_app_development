from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.models import Note, Exam, Question, Answer
from app.services import generate_questions, analyze_weakness
from app.utils import login_required

exam_bp = Blueprint('exams', __name__, url_prefix='/exams')


@exam_bp.route('/generate/<int:note_id>', methods=['POST'])
@login_required
def generate_exam(note_id):
    """AI 根據筆記摘要出題，建立測驗。"""
    user_id = session['user_id']
    note    = Note.get_by_id(note_id)

    if note is None:
        abort(404)
    if note.user_id != user_id:
        abort(403)
    if not note.summary:
        flash('請先等待筆記整理完成才能出題', 'warning')
        return redirect(url_for('notes.view_note', note_id=note_id))

    # 呼叫 AI 出題
    questions_data = generate_questions(note.summary)
    if not questions_data:
        flash('AI 出題服務暫時無法使用，請稍後再試', 'danger')
        return redirect(url_for('notes.view_note', note_id=note_id))

    # 建立 Exam 與 Question 紀錄
    exam = Exam.create(note_id=note_id, user_id=user_id, total_questions=len(questions_data))
    if exam is None:
        flash('建立測驗失敗，請稍後再試', 'danger')
        return redirect(url_for('notes.view_note', note_id=note_id))

    Question.bulk_create(exam.id, questions_data)
    flash('測驗已生成，開始作答！', 'success')
    return redirect(url_for('exams.take_exam', exam_id=exam.id))


@exam_bp.route('/<int:exam_id>', methods=['GET'])
@login_required
def take_exam(exam_id):
    """顯示測驗作答頁面。"""
    user_id = session['user_id']
    exam    = Exam.get_by_id(exam_id)

    if exam is None:
        abort(404)
    if exam.user_id != user_id:
        abort(403)

    # 已作答過 → redirect 至成績頁
    if exam.score is not None:
        return redirect(url_for('exams.exam_result', exam_id=exam_id))

    questions = Question.get_by_exam(exam_id)
    return render_template('exams/take_exam.html', exam=exam, questions=questions)


@exam_bp.route('/submit/<int:exam_id>', methods=['POST'])
@login_required
def submit_exam(exam_id):
    """送出作答並批改。"""
    user_id = session['user_id']
    exam    = Exam.get_by_id(exam_id)

    if exam is None:
        abort(404)
    if exam.user_id != user_id:
        abort(403)
    if exam.score is not None:
        return redirect(url_for('exams.exam_result', exam_id=exam_id))

    questions   = Question.get_by_exam(exam_id)
    score       = 0
    answers_data = []

    for q in questions:
        user_ans  = request.form.get(f'answer_{q.id}', '').upper()
        is_correct = (user_ans == q.correct_answer)
        if is_correct:
            score += 1
        answers_data.append({
            'exam_id':     exam_id,
            'question_id': q.id,
            'user_answer': user_ans or 'A',   # 未作答預設 'A'（算錯）
            'is_correct':  is_correct,
        })

    Answer.bulk_create(answers_data)
    exam.submit(score)
    flash(f'測驗完成！答對 {score}/{exam.total_questions} 題', 'success')
    return redirect(url_for('exams.exam_result', exam_id=exam_id))


@exam_bp.route('/result/<int:exam_id>', methods=['GET'])
@login_required
def exam_result(exam_id):
    """顯示成績解析與 AI 弱點分析。"""
    user_id = session['user_id']
    exam    = Exam.get_by_id(exam_id)

    if exam is None:
        abort(404)
    if exam.user_id != user_id:
        abort(403)
    if exam.score is None:
        return redirect(url_for('exams.take_exam', exam_id=exam_id))

    answers   = Answer.get_by_exam(exam_id)
    questions = {q.id: q for q in Question.get_by_exam(exam_id)}

    # 整合問題資訊到答案
    for ans in answers:
        ans.question = questions.get(ans.question_id)

    # AI 弱點分析
    wrong_questions = [
        {'question_text': ans.question.question_text, 'explanation': ans.question.explanation}
        for ans in answers
        if not ans.is_correct and ans.question
    ]
    weakness_advice = analyze_weakness(wrong_questions) if wrong_questions else ''

    return render_template(
        'exams/result.html',
        exam=exam,
        answers=answers,
        weakness_advice=weakness_advice,
    )
