from app import db
from datetime import datetime


class Note(db.Model):
    """筆記資料 Model"""
    __tablename__ = 'note'

    id          = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    user_id     = db.Column(db.Integer,      db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title       = db.Column(db.String(200),  nullable=False)
    raw_content = db.Column(db.Text,         nullable=False)
    summary     = db.Column(db.Text,         nullable=True)   # AI 整理後才填入
    created_at  = db.Column(db.DateTime,     nullable=False, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,     nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exams = db.relationship('Exam', backref='source_note', lazy=True, cascade='all, delete-orphan')

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, user_id: int, title: str, raw_content: str, summary: str = None) -> 'Note':
        """建立新筆記並寫入資料庫"""
        note = cls(
            user_id=user_id,
            title=title,
            raw_content=raw_content,
            summary=summary
        )
        db.session.add(note)
        db.session.commit()
        return note

    @classmethod
    def get_all(cls) -> list['Note']:
        """取得所有筆記（管理用）"""
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_user(cls, user_id: int) -> list['Note']:
        """取得某使用者的所有筆記（最新在前）"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_id(cls, note_id: int) -> 'Note | None':
        """以 ID 查詢單一筆記"""
        return cls.query.get(note_id)

    def update(self, title: str = None, raw_content: str = None, summary: str = None) -> 'Note':
        """更新筆記內容"""
        if title is not None:
            self.title = title
        if raw_content is not None:
            self.raw_content = raw_content
        if summary is not None:
            self.summary = summary
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

    def delete(self) -> None:
        """刪除此筆記（關聯測驗 CASCADE 刪除）"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f'<Note id={self.id} title={self.title!r} user_id={self.user_id}>'
