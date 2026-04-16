from app import db
from datetime import datetime


class Question(db.Model):
    """
    測驗題目 Model。

    Attributes:
        id:             主鍵，自動遞增。
        exam_id:        外鍵，對應 exam.id。
        question_text:  題目內容。
        option_a~d:     四個選項文字。
        correct_answer: 正確答案（'A'、'B'、'C' 或 'D'）。
        explanation:    AI 提供的解析說明。
    """
    __tablename__ = 'question'

    id             = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    exam_id        = db.Column(db.Integer,     db.ForeignKey('exam.id', ondelete='CASCADE'), nullable=False)
    question_text  = db.Column(db.Text,        nullable=False)
    option_a       = db.Column(db.String(300), nullable=False)
    option_b       = db.Column(db.String(300), nullable=False)
    option_c       = db.Column(db.String(300), nullable=False)
    option_d       = db.Column(db.String(300), nullable=False)
    correct_answer = db.Column(db.String(1),   nullable=False)
    explanation    = db.Column(db.Text,        nullable=True)

    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, exam_id: int, question_text: str,
               option_a: str, option_b: str, option_c: str, option_d: str,
               correct_answer: str, explanation: str = None) -> 'Question | None':
        """
        建立單一題目。

        Args:
            exam_id:        所屬測驗 ID。
            question_text:  題目內容。
            option_a~d:     四個選項。
            correct_answer: 正確答案字母（'A'~'D'）。
            explanation:    解析說明（可選）。

        Returns:
            成功：Question 物件；失敗：None。
        """
        try:
            question = cls(
                exam_id=exam_id,
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer.upper(),
                explanation=explanation
            )
            db.session.add(question)
            db.session.commit()
            return question
        except Exception as e:
            db.session.rollback()
            print(f"[Question.create] 失敗：{e}")
            return None

    @classmethod
    def bulk_create(cls, exam_id: int, questions_data: list[dict]) -> list['Question']:
        """
        批次建立多道題目（AI 出題後使用）。

        Args:
            exam_id:        所屬測驗 ID。
            questions_data: 題目字典清單，每個字典含：
                            question_text, option_a, option_b, option_c,
                            option_d, correct_answer, explanation（可選）。

        Returns:
            成功：Question 物件清單；失敗：空清單。
        """
        try:
            questions = [
                cls(
                    exam_id=exam_id,
                    question_text=q['question_text'],
                    option_a=q['option_a'],
                    option_b=q['option_b'],
                    option_c=q['option_c'],
                    option_d=q['option_d'],
                    correct_answer=q['correct_answer'].upper(),
                    explanation=q.get('explanation')
                )
                for q in questions_data
            ]
            db.session.add_all(questions)
            db.session.commit()
            return questions
        except Exception as e:
            db.session.rollback()
            print(f"[Question.bulk_create] 失敗：{e}")
            return []

    @classmethod
    def get_all(cls) -> list['Question']:
        """取得所有題目（管理用）。"""
        try:
            return cls.query.all()
        except Exception as e:
            print(f"[Question.get_all] 失敗：{e}")
            return []

    @classmethod
    def get_by_id(cls, question_id: int) -> 'Question | None':
        """
        以 ID 查詢單一題目。

        Args:
            question_id: 題目主鍵。

        Returns:
            Question 物件或 None。
        """
        try:
            return db.session.get(cls, question_id)
        except Exception as e:
            print(f"[Question.get_by_id] 失敗：{e}")
            return None

    @classmethod
    def get_by_exam(cls, exam_id: int) -> list['Question']:
        """
        取得某場測驗的所有題目。

        Args:
            exam_id: 測驗主鍵。

        Returns:
            Question 物件清單。
        """
        try:
            return cls.query.filter_by(exam_id=exam_id).all()
        except Exception as e:
            print(f"[Question.get_by_exam] 失敗：{e}")
            return []

    def update(self, **kwargs) -> bool:
        """
        更新題目欄位。

        Args:
            **kwargs: 欄位名稱與新值（例如 explanation='...'）。

        Returns:
            True：更新成功；False：更新失敗。
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key) and value is not None:
                    setattr(self, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Question.update] 失敗：{e}")
            return False

    def delete(self) -> bool:
        """
        刪除此題目。

        Returns:
            True：刪除成功；False：刪除失敗。
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Question.delete] 失敗：{e}")
            return False

    def __repr__(self) -> str:
        return f'<Question id={self.id} exam_id={self.exam_id}>'


class Exam(db.Model):
    """
    測驗紀錄 Model。

    Attributes:
        id:              主鍵，自動遞增。
        note_id:         外鍵，對應 note.id（來源筆記）。
        user_id:         外鍵，對應 user.id（作答學生）。
        score:           答對題數（送出後才填入，初始為 None）。
        total_questions: 本次測驗總題數。
        taken_at:        作答送出時間。
    """
    __tablename__ = 'exam'

    id              = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    note_id         = db.Column(db.Integer,  db.ForeignKey('note.id', ondelete='CASCADE'), nullable=False)
    user_id         = db.Column(db.Integer,  db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    score           = db.Column(db.Integer,  nullable=True)
    total_questions = db.Column(db.Integer,  nullable=False)
    taken_at        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', backref='exam', lazy=True, cascade='all, delete-orphan')
    answers   = db.relationship('Answer',   backref='exam', lazy=True, cascade='all, delete-orphan')

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, note_id: int, user_id: int, total_questions: int) -> 'Exam | None':
        """
        建立新測驗紀錄（題目由 Question.bulk_create 另行寫入）。

        Args:
            note_id:         來源筆記 ID。
            user_id:         作答學生 ID。
            total_questions: 本次測驗題數。

        Returns:
            成功：Exam 物件；失敗：None。
        """
        try:
            exam = cls(note_id=note_id, user_id=user_id, total_questions=total_questions)
            db.session.add(exam)
            db.session.commit()
            return exam
        except Exception as e:
            db.session.rollback()
            print(f"[Exam.create] 失敗：{e}")
            return None

    @classmethod
    def get_all(cls) -> list['Exam']:
        """取得所有測驗紀錄（管理用），依作答時間倒序。"""
        try:
            return cls.query.order_by(cls.taken_at.desc()).all()
        except Exception as e:
            print(f"[Exam.get_all] 失敗：{e}")
            return []

    @classmethod
    def get_by_id(cls, exam_id: int) -> 'Exam | None':
        """
        以 ID 查詢單一測驗。

        Args:
            exam_id: 測驗主鍵。

        Returns:
            Exam 物件或 None。
        """
        try:
            return db.session.get(cls, exam_id)
        except Exception as e:
            print(f"[Exam.get_by_id] 失敗：{e}")
            return None

    @classmethod
    def get_by_user(cls, user_id: int) -> list['Exam']:
        """
        取得某使用者所有測驗，依作答時間倒序。

        Args:
            user_id: 使用者主鍵。

        Returns:
            Exam 物件清單。
        """
        try:
            return cls.query.filter_by(user_id=user_id).order_by(cls.taken_at.desc()).all()
        except Exception as e:
            print(f"[Exam.get_by_user] 失敗：{e}")
            return []

    @classmethod
    def get_by_note(cls, note_id: int) -> list['Exam']:
        """
        取得某篇筆記衍生的所有測驗，依作答時間倒序。

        Args:
            note_id: 筆記主鍵。

        Returns:
            Exam 物件清單。
        """
        try:
            return cls.query.filter_by(note_id=note_id).order_by(cls.taken_at.desc()).all()
        except Exception as e:
            print(f"[Exam.get_by_note] 失敗：{e}")
            return []

    def submit(self, score: int) -> bool:
        """
        填入批改後的分數，並更新 taken_at 為送出當下時間。

        Args:
            score: 答對題數。

        Returns:
            True：儲存成功；False：儲存失敗。
        """
        try:
            self.score = score
            self.taken_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Exam.submit] 失敗：{e}")
            return False

    def update(self, score: int = None, total_questions: int = None) -> bool:
        """
        更新測驗紀錄欄位。

        Args:
            score:           新分數（可選）。
            total_questions: 新總題數（可選）。

        Returns:
            True：更新成功；False：更新失敗。
        """
        try:
            if score is not None:
                self.score = score
            if total_questions is not None:
                self.total_questions = total_questions
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Exam.update] 失敗：{e}")
            return False

    def delete(self) -> bool:
        """
        刪除此測驗（關聯題目與作答 CASCADE 刪除）。

        Returns:
            True：刪除成功；False：刪除失敗。
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Exam.delete] 失敗：{e}")
            return False

    @property
    def percentage(self) -> float | None:
        """計算答對百分比（0.0 ~ 100.0），尚未作答時回傳 None。"""
        if self.score is None or self.total_questions == 0:
            return None
        return round(self.score / self.total_questions * 100, 1)

    def __repr__(self) -> str:
        return f'<Exam id={self.id} score={self.score}/{self.total_questions}>'


class Answer(db.Model):
    """
    使用者作答紀錄 Model。

    Attributes:
        id:          主鍵，自動遞增。
        exam_id:     外鍵，對應 exam.id。
        question_id: 外鍵，對應 question.id。
        user_answer: 學生選擇的答案（'A'~'D'）。
        is_correct:  是否答對。
    """
    __tablename__ = 'answer'

    id          = db.Column(db.Integer,   primary_key=True, autoincrement=True)
    exam_id     = db.Column(db.Integer,   db.ForeignKey('exam.id',     ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer,   db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False)
    user_answer = db.Column(db.String(1), nullable=False)
    is_correct  = db.Column(db.Boolean,   nullable=False, default=False)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, exam_id: int, question_id: int, user_answer: str, is_correct: bool) -> 'Answer | None':
        """
        建立單筆作答紀錄。

        Args:
            exam_id:     所屬測驗 ID。
            question_id: 所屬題目 ID。
            user_answer: 學生作答字母（'A'~'D'）。
            is_correct:  是否答對。

        Returns:
            成功：Answer 物件；失敗：None。
        """
        try:
            answer = cls(
                exam_id=exam_id,
                question_id=question_id,
                user_answer=user_answer.upper(),
                is_correct=is_correct
            )
            db.session.add(answer)
            db.session.commit()
            return answer
        except Exception as e:
            db.session.rollback()
            print(f"[Answer.create] 失敗：{e}")
            return None

    @classmethod
    def bulk_create(cls, answers_data: list[dict]) -> list['Answer']:
        """
        批次建立作答紀錄（送出測驗時使用）。

        Args:
            answers_data: 作答字典清單，每個字典含：
                          exam_id, question_id, user_answer, is_correct。

        Returns:
            成功：Answer 物件清單；失敗：空清單。
        """
        try:
            records = [
                cls(
                    exam_id=a['exam_id'],
                    question_id=a['question_id'],
                    user_answer=a['user_answer'].upper(),
                    is_correct=a['is_correct']
                )
                for a in answers_data
            ]
            db.session.add_all(records)
            db.session.commit()
            return records
        except Exception as e:
            db.session.rollback()
            print(f"[Answer.bulk_create] 失敗：{e}")
            return []

    @classmethod
    def get_all(cls) -> list['Answer']:
        """取得所有作答紀錄（管理用）。"""
        try:
            return cls.query.all()
        except Exception as e:
            print(f"[Answer.get_all] 失敗：{e}")
            return []

    @classmethod
    def get_by_id(cls, answer_id: int) -> 'Answer | None':
        """
        以 ID 查詢單筆作答。

        Args:
            answer_id: 作答紀錄主鍵。

        Returns:
            Answer 物件或 None。
        """
        try:
            return db.session.get(cls, answer_id)
        except Exception as e:
            print(f"[Answer.get_by_id] 失敗：{e}")
            return None

    @classmethod
    def get_by_exam(cls, exam_id: int) -> list['Answer']:
        """
        取得某場測驗的所有作答紀錄。

        Args:
            exam_id: 測驗主鍵。

        Returns:
            Answer 物件清單。
        """
        try:
            return cls.query.filter_by(exam_id=exam_id).all()
        except Exception as e:
            print(f"[Answer.get_by_exam] 失敗：{e}")
            return []

    @classmethod
    def get_wrong_answers(cls, user_id: int) -> list['Answer']:
        """
        取得某使用者所有答錯的紀錄（弱點分析用）。

        Args:
            user_id: 使用者主鍵。

        Returns:
            is_correct=False 的 Answer 物件清單。
        """
        try:
            return (
                cls.query
                .join(Exam, cls.exam_id == Exam.id)
                .filter(Exam.user_id == user_id, cls.is_correct == False)  # noqa: E712
                .all()
            )
        except Exception as e:
            print(f"[Answer.get_wrong_answers] 失敗：{e}")
            return []

    def update(self, user_answer: str = None, is_correct: bool = None) -> bool:
        """
        更新作答紀錄。

        Args:
            user_answer: 新作答字母（可選）。
            is_correct:  新正確與否（可選）。

        Returns:
            True：更新成功；False：更新失敗。
        """
        try:
            if user_answer is not None:
                self.user_answer = user_answer.upper()
            if is_correct is not None:
                self.is_correct = is_correct
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Answer.update] 失敗：{e}")
            return False

    def delete(self) -> bool:
        """
        刪除此作答紀錄。

        Returns:
            True：刪除成功；False：刪除失敗。
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Answer.delete] 失敗：{e}")
            return False

    def __repr__(self) -> str:
        return f'<Answer id={self.id} q={self.question_id} ans={self.user_answer} correct={self.is_correct}>'
