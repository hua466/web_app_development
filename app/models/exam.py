from app import db
from datetime import datetime


class Question(db.Model):
    """測驗題目 Model"""
    __tablename__ = 'question'

    id              = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    exam_id         = db.Column(db.Integer,      db.ForeignKey('exam.id', ondelete='CASCADE'), nullable=False)
    question_text   = db.Column(db.Text,         nullable=False)
    option_a        = db.Column(db.String(300),  nullable=False)
    option_b        = db.Column(db.String(300),  nullable=False)
    option_c        = db.Column(db.String(300),  nullable=False)
    option_d        = db.Column(db.String(300),  nullable=False)
    correct_answer  = db.Column(db.String(1),    nullable=False)   # 'A' | 'B' | 'C' | 'D'
    explanation     = db.Column(db.Text,         nullable=True)

    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, exam_id: int, question_text: str,
               option_a: str, option_b: str, option_c: str, option_d: str,
               correct_answer: str, explanation: str = None) -> 'Question':
        """建立單一題目"""
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

    @classmethod
    def bulk_create(cls, exam_id: int, questions_data: list[dict]) -> list['Question']:
        """批次建立多道題目（AI 出題後使用）

        questions_data 格式範例：
        [
            {
                "question_text": "...",
                "option_a": "...", "option_b": "...",
                "option_c": "...", "option_d": "...",
                "correct_answer": "A",
                "explanation": "..."
            },
            ...
        ]
        """
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

    @classmethod
    def get_all(cls) -> list['Question']:
        """取得所有題目（管理用）"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, question_id: int) -> 'Question | None':
        """以 ID 查詢單一題目"""
        return cls.query.get(question_id)

    @classmethod
    def get_by_exam(cls, exam_id: int) -> list['Question']:
        """取得某場測驗的所有題目"""
        return cls.query.filter_by(exam_id=exam_id).all()

    def update(self, **kwargs) -> 'Question':
        """更新欄位（傳入欄位名稱與值）"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self) -> None:
        """刪除此題目"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f'<Question id={self.id} exam_id={self.exam_id}>'


class Exam(db.Model):
    """測驗紀錄 Model"""
    __tablename__ = 'exam'

    id              = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    note_id         = db.Column(db.Integer,  db.ForeignKey('note.id', ondelete='CASCADE'), nullable=False)
    user_id         = db.Column(db.Integer,  db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    score           = db.Column(db.Integer,  nullable=True)    # 送出後才填入
    total_questions = db.Column(db.Integer,  nullable=False)
    taken_at        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', backref='exam', lazy=True, cascade='all, delete-orphan')
    answers   = db.relationship('Answer',   backref='exam', lazy=True, cascade='all, delete-orphan')

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, note_id: int, user_id: int, total_questions: int) -> 'Exam':
        """建立新測驗紀錄（題目尚未產出）"""
        exam = cls(note_id=note_id, user_id=user_id, total_questions=total_questions)
        db.session.add(exam)
        db.session.commit()
        return exam

    @classmethod
    def get_all(cls) -> list['Exam']:
        """取得所有測驗紀錄（管理用）"""
        return cls.query.order_by(cls.taken_at.desc()).all()

    @classmethod
    def get_by_id(cls, exam_id: int) -> 'Exam | None':
        """以 ID 查詢單一測驗"""
        return cls.query.get(exam_id)

    @classmethod
    def get_by_user(cls, user_id: int) -> list['Exam']:
        """取得某使用者所有測驗（最新在前）"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.taken_at.desc()).all()

    @classmethod
    def get_by_note(cls, note_id: int) -> list['Exam']:
        """取得某篇筆記衍生的所有測驗"""
        return cls.query.filter_by(note_id=note_id).order_by(cls.taken_at.desc()).all()

    def submit(self, score: int) -> 'Exam':
        """填入批改後的分數"""
        self.score = score
        self.taken_at = datetime.utcnow()
        db.session.commit()
        return self

    def update(self, score: int = None, total_questions: int = None) -> 'Exam':
        """更新測驗紀錄"""
        if score is not None:
            self.score = score
        if total_questions is not None:
            self.total_questions = total_questions
        db.session.commit()
        return self

    def delete(self) -> None:
        """刪除此測驗（關聯題目與作答 CASCADE 刪除）"""
        db.session.delete(self)
        db.session.commit()

    @property
    def percentage(self) -> float | None:
        """計算答對百分比"""
        if self.score is None or self.total_questions == 0:
            return None
        return round(self.score / self.total_questions * 100, 1)

    def __repr__(self) -> str:
        return f'<Exam id={self.id} score={self.score}/{self.total_questions}>'


class Answer(db.Model):
    """使用者作答紀錄 Model"""
    __tablename__ = 'answer'

    id          = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    exam_id     = db.Column(db.Integer,  db.ForeignKey('exam.id',     ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer,  db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False)
    user_answer = db.Column(db.String(1), nullable=False)   # 'A' | 'B' | 'C' | 'D'
    is_correct  = db.Column(db.Boolean,  nullable=False, default=False)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, exam_id: int, question_id: int, user_answer: str, is_correct: bool) -> 'Answer':
        """建立單筆作答紀錄"""
        answer = cls(
            exam_id=exam_id,
            question_id=question_id,
            user_answer=user_answer.upper(),
            is_correct=is_correct
        )
        db.session.add(answer)
        db.session.commit()
        return answer

    @classmethod
    def bulk_create(cls, answers_data: list[dict]) -> list['Answer']:
        """批次建立作答紀錄（送出測驗時使用）

        answers_data 格式範例：
        [
            {"exam_id": 1, "question_id": 3, "user_answer": "B", "is_correct": False},
            ...
        ]
        """
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

    @classmethod
    def get_all(cls) -> list['Answer']:
        """取得所有作答紀錄（管理用）"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, answer_id: int) -> 'Answer | None':
        """以 ID 查詢單筆作答"""
        return cls.query.get(answer_id)

    @classmethod
    def get_by_exam(cls, exam_id: int) -> list['Answer']:
        """取得某場測驗的所有作答紀錄"""
        return cls.query.filter_by(exam_id=exam_id).all()

    @classmethod
    def get_wrong_answers(cls, user_id: int) -> list['Answer']:
        """取得某使用者所有答錯的紀錄（弱點分析用）"""
        return (
            cls.query
            .join(Exam, cls.exam_id == Exam.id)
            .filter(Exam.user_id == user_id, cls.is_correct == False)
            .all()
        )

    def update(self, user_answer: str = None, is_correct: bool = None) -> 'Answer':
        """更新作答紀錄"""
        if user_answer is not None:
            self.user_answer = user_answer.upper()
        if is_correct is not None:
            self.is_correct = is_correct
        db.session.commit()
        return self

    def delete(self) -> None:
        """刪除此作答紀錄"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f'<Answer id={self.id} q={self.question_id} ans={self.user_answer} correct={self.is_correct}>'
